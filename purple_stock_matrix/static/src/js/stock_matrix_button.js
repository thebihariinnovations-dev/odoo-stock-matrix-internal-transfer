/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ProductMatrixDialog } from "@product_matrix/js/product_matrix_dialog";
import { Component } from "@odoo/owl";

export class StockMatrixButton extends Component {
    static template = "purple_stock_matrix.StockMatrixButton";
    static props = {
        record: Object,
        readonly: { type: Boolean, optional: true },
        id: { type: String, optional: true },
        name: { type: String, optional: true },
        "*": true,
    };

    setup() {
        this.dialog = useService("dialog");
    }

    async openMatrixDialog() {
        const record = this.props.record;
        const productTmplId = record.data.grid_product_tmpl_id;

        if (!productTmplId || !productTmplId.id) {
            alert("Please select a Product Template first!");
            return;
        }

        // Force reload grid by resetting and re-setting product
        await record.update({ grid_product_tmpl_id: false });
        await record.update({ grid_product_tmpl_id: productTmplId });

        const gridData = record.data.grid;
        if (!gridData) {
            alert("Grid data not loaded. Please try again.");
            return;
        }

        const infos = JSON.parse(gridData);

        this.dialog.add(ProductMatrixDialog, {
            header: infos.header,
            rows: infos.matrix,
            editedCellAttributes: "",
            product_template_id: infos.product_template_id,
            record: record,
        });
    }
}

registry.category("fields").add("stock_matrix_button", {
    component: StockMatrixButton,
});
