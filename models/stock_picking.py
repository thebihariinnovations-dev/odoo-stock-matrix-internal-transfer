import json
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    grid_product_tmpl_id = fields.Many2one(
        'product.template',
        store=False,
        help="Technical field for product matrix on internal transfers.",
    )
    grid_update = fields.Boolean(
        default=False,
        store=False,
        help="Whether grid contains new matrix to apply.",
    )
    grid = fields.Char(
        store=False,
        help="Technical storage of grid data.",
    )

    @api.onchange('grid_product_tmpl_id')
    def _set_grid_up(self):
        if self.grid_product_tmpl_id:
            self.grid_update = False
            matrix = self._get_stock_matrix(self.grid_product_tmpl_id)
            matrix['product_template_id'] = self.grid_product_tmpl_id.id
            self.grid = json.dumps(matrix)

    @api.onchange('grid')
    def _apply_grid(self):
        if not self.grid or not self.grid_update:
            return

        grid = json.loads(self.grid)
        product_template = self.env['product.template'].browse(
            grid['product_template_id']
        )
        dirty_cells = grid['changes']
        Attrib = self.env['product.template.attribute.value']

        new_move_vals = []

        for cell in dirty_cells:
            combination = Attrib.browse(cell['ptav_ids'])
            product = product_template._create_product_variant(combination)
            if not product:
                continue

            qty = cell['qty']
            if qty <= 0:
                continue

            # Check if move already exists for this product
            existing_moves = self.move_ids.filtered(
                lambda m: (m._origin or m).product_id == product
            )

            if existing_moves:
                existing_moves[0].product_uom_qty = qty
            else:
                new_move_vals.append({
                    # 'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'product_uom': product.uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'picking_id': self._origin.id if self._origin else False,
                })

        if new_move_vals:
            self.update({
                'move_ids': [(0, 0, vals) for vals in new_move_vals]
            })

    def _get_stock_matrix(self, product_template):
        matrix = product_template._get_template_matrix(
            company_id=self.company_id,
            currency_id=self.env.company.currency_id,
        )
        if self.move_ids:
            lines = matrix['matrix']
            moves = self.move_ids.filtered(
                lambda m: m.product_id.product_tmpl_id == product_template
            )
            for row in lines:
                for cell in row:
                    if not cell.get('name', False):
                        ptav_ids = sorted(cell['ptav_ids'])
                        matched_moves = moves.filtered(
                            lambda m: sorted(
                                m.product_id.product_template_attribute_value_ids.ids
                            ) == ptav_ids
                        )
                        if matched_moves:
                            cell['qty'] = sum(
                                matched_moves.mapped('product_uom_qty')
                            )
        return matrix
