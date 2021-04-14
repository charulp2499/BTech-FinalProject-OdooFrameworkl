# -*- coding: utf-8 -*-
{
    'name': "Placement Portal",
    'description': """
        Placement Portal
    """,
    'depends': ['portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset.xml',
        'views/assets.xml',
        'views/view_home.xml',
        'views/view_student.xml',
        'views/view_faculty.xml',
        'views/login.xml',
        'views/forgot_pwd.xml',
        'views/aview_index.xml',
        'views/aview_change_pwd.xml',
        'views/aview_department_data.xml',
        'views/aview_faculites_list.xml',
        'views/aview_student_list.xml',
        'views/aview_user_res_form.xml',
        'views/aview_department_add_form.xml',
        'views/fview_home.xml',
        'views/fview_student_list.xml',
        'views/fview_edit_profile.xml',
        'views/fview_change_pwd.xml',
        'views/fview_user_add.xml',
        'views/sview_home.xml',
        'views/sview_edit_profile.xml',
        'views/sview_change_pwd.xml',
        'views/placement.xml',
        'views/server_users_data.xml',
        'views/server_department_data.xml',
        'views/server_user_login.xml',  
        'views/aview_deactive.xml',     
    ],
    'demo': [
    ],
    'application': True
}