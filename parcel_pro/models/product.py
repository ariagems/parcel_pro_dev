# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):

    _inherit = "product.product"

    height = fields.Float(
        'Height', digits=dp.get_precision('Stock Height'),
        help="The height of the contents in Kg, not including any packaging, etc.")

    length = fields.Float(
        'Length', digits=dp.get_precision('Stock Length'),
        help="The height of the contents in Kg, not including any packaging, etc.")

    width = fields.Float(
        'Width', digits=dp.get_precision('Stock Width'),
        help="The height of the contents in Kg, not including any packaging, etc.")


class ProductTemplate(models.Model):

    _inherit = "product.template"

    height = fields.Float(
        'Height', compute='_compute_height', digits=dp.get_precision('Stock Height'),
        inverse='_set_height', store=True,
        help="The height of the contents in Kg, not including any packaging, etc.")

    length = fields.Float(
        'Length', compute='_compute_length', digits=dp.get_precision('Stock Length'),
        inverse='_set_length', store=True,
        help="The length of the contents in Kg, not including any packaging, etc.")

    width = fields.Float(
        'Width', compute='_compute_width', digits=dp.get_precision('Stock Width'),
        inverse='_set_width', store=True,
        help="The width of the contents in Kg, not including any packaging, etc.")

    @api.depends('product_variant_ids', 'product_variant_ids.height')
    def _compute_height(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.height = template.product_variant_ids.height
        for template in (self - unique_variants):
            template.height = 0.0

    @api.depends('product_variant_ids', 'product_variant_ids.height')
    def _compute_length(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.length = template.product_variant_ids.length
        for template in (self - unique_variants):
            template.length = 0.0

    @api.depends('product_variant_ids', 'product_variant_ids.height')
    def _compute_width(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.width = template.product_variant_ids.width
        for template in (self - unique_variants):
            template.width = 0.0

    @api.one
    def _set_height(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.height = self.height

    @api.one
    def _set_length(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.length = self.length

    @api.one
    def _set_width(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.width = self.width

    @api.model
    def create(self, vals):
        rel_vals = {}
        template = super(ProductTemplate, self).create(vals)
        rel_vals['length'] = vals['length']
        if rel_vals:
            template.write(rel_vals)
        return template




