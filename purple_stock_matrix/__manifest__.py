{
    'name': 'Purple Stock Matrix',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Add stock move lines via product variant matrix on Internal Transfers',
    'depends': ['stock', 'product_matrix'],
    'assets': {
        'web.assets_backend': [
            'purple_stock_matrix/static/src/js/stock_matrix_button.js',
            'purple_stock_matrix/static/src/xml/stock_matrix_button.xml',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_form_view.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
