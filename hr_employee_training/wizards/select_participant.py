# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class SelectTrainingParticipant(models.TransientModel):
    _name = "hr.select_training_participant"
    _description = "Select Training Participant"

    @api.model
    def _default_training_id(self):
        return self.env.context.get("active_id", False)

    training_id = fields.Many2one(
        string="Training",
        comodel_name="hr.training",
        required=True,
        default=lambda self: self._default_training_id(),
    )
    employee_ids = fields.Many2many(
        string="Employee",
        comodel_name="hr.employee",
        relation="rel_select_participant_2_employee",
        column1="wizard_id",
        column2="employee_id",
        required=True,
    )

    @api.multi
    def action_select_participant(self):
        for wiz in self:
            wiz._select_participant()

    @api.multi
    def _select_participant(self):
        self.ensure_one()
        obj_training = self.env["hr.training"]
        training_id = self.env.context.get("active_id", False)
        training = obj_training.browse([training_id])[0]
        training.write(self._prepare_write_data())

    @api.multi
    def _prepare_write_data(self):
        self.ensure_one()
        list_participant = []
        for employee in self.employee_ids:
            criteria = [
                ("training_id", "=", self.training_id.id),
                ("partisipant_id", "=", employee.id),
            ]
            if self.env["hr.training_partisipant"].search_count(criteria) > 0:
                continue

            data = {
                "partisipant_id": employee.id,
                "job_id": employee.job_id and employee.job_id.id or False,
            }
            list_participant.append((0, 0, data))
        result = {
            "partisipant_ids": list_participant,
        }
        return result
