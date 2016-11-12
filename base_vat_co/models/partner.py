# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    John W. Viloria Amaris <john.viloria.amaris@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = ['res.partner']

    @api.constrains("vat")
    def check_vat(self):
        '''
        Check the VAT number depending of the country.
        http://sima-pc.com/nif.php
        '''
        for partner in self:
            if not partner.vat:
                continue
            if partner.country_id:
                vat_country = partner.country_id.code.lower()
                vat_number = partner.vat
            else:
                vat_country, vat_number = self._split_vat(partner.vat)
            if not hasattr(self, 'check_vat_' + vat_country):
                continue
            check = getattr(self, 'check_vat_' + vat_country)
            if not check(vat_number):
                raise ValidationError(
                    _('The Vat does not seems to be correct.')
                )

    def check_vat_co(self, vat):
        '''
        Check VAT Routine for Colombia.
        '''
        if type(vat) == str:
            vat = vat.replace('-', '', 1).replace('.', '', 2)
        if len(str(vat)) < 4:
            return False
        try:
            int(vat)
        except ValueError:
            return False
        #Validación Nit Terceros del exterior
        if len(str(vat)) == 9 and str(vat)[0:5] == '44444' \
                and int(str(vat)[5:]) <= 9000 \
                and int(str(vat)[5:]) >= 4001:
            return True
        prime = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
        sum = 0
        vat_len = len(str(vat))
        for i in range(vat_len - 2, -1, -1):
            sum += int(str(vat)[i]) * prime[vat_len - 2 - i]
        if sum % 11 > 1:
            return str(vat)[vat_len - 1] == str(11 - (sum % 11))
        else:
            return str(vat)[vat_len - 1] == str(sum % 11)