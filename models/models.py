from odoo import models, fields, api
from odoo.exceptions import ValidationError

class placement(models.Model):
    _name = 'placement.portal.placement'
    _description = "Placement Details"

class user_login(models.Model):
    _name = 'placement.portal.user.login'
    _description = "User Login Details"

    email=fields.Char(string='Email', required=True)
    password=fields.Char(string='password', required=True)
    types=fields.Char(string='User Type', required=True)
    active=fields.Boolean(default=True)


    _sql_constraints = [
        ('email_uniq', 'unique (email)', 'Already In Use !!!')
    ]

class department_data(models.Model):
    _name = 'placement.portal.department.data'
    _description = "Department Details"

    name=fields.Char('Department Name')
    code=fields.Char('Department Code')


    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Already In Use !!!')
    ]

class users_data(models.Model):
    _name = 'placement.portal.users.data'
    _description = "Users Details"

    name=fields.Char('Name')
    img=fields.Binary('Image')
    department=fields.Many2one("placement.portal.department.data")
    dob=fields.Date('Date Of Birth')
    email=fields.Char('E Mail')
    pass_out_year=fields.Integer('Pass-Out Year')
    education=fields.Char('Education')
    location=fields.Char('Location')
    skills=fields.Char('Skills')
    note=fields.Char('Note')
    types=fields.Char('Type')
    user_id=fields.Many2one("placement.portal.user.login")
    facebook=fields.Char('Facebook Link')
    instagram=fields.Char('instagram Link')
    linkedin=fields.Char('Linked-In Link')
    active=fields.Boolean(default=True)
    timeline_ids=fields.One2many("placement.portal.time.line", 'user_id')

class time_line(models.Model):
    _name = 'placement.portal.time.line'
    _description = "Users Details"
    _order="start_date desc"

    user_id=fields.Many2one("placement.portal.users.data")
    cname=fields.Char('company Name')
    job_des=fields.Char('Job Description')
    start_date=fields.Date('Starting Date')
    end_date=fields.Date('Ending Date')