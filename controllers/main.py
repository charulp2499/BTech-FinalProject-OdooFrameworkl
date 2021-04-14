from odoo import http, api, fields, models, _
from odoo.http import request
import base64
from odoo.exceptions import UserError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime

class Main(CustomerPortal):

    #WebSite Pages
    @http.route(['/mainpage'], auth='public', type="http", website=True)
    def mainpage(self, **kw):
        departments=request.env['placement.portal.department.data'].sudo().search([])
        return request.render("placement_portal.mainpage", {'departments': departments})  

    @http.route(['/viewstudentlist', '/sort/<string:order_by>/<string:filters>'], auth='public', type="http", website=True)
    def viewstudentlist(self, order_by=None, filters=None, **kw):
        students=request.env['placement.portal.users.data'].sudo().search([])
        students = students.filtered(lambda c: c.types == 'Student')
        timelines = dict()
        filter = {'year': [], 'department': []}
        for student in students:
            timelines[student.id] = request.env['placement.portal.users.data'].timeline_ids.sudo().search([('user_id', '=', student.id)],order="start_date asc")
            not student.pass_out_year in filter.get("year") and student.pass_out_year != 0 and filter.get("year").append(student.pass_out_year)
            not student.department in filter.get("department") and filter.get("department").append(student.department)
        # import pdb; pdb.set_trace()
        return request.render("placement_portal.viewstudentlist",{'students': students, 'timelines' : timelines, 'year': filter.get('year'), 'department': filter.get('department') })

    @http.route(['/viewfacultylist'], auth='public', type="http", website=True)
    def viewfacultylist(self, **kw):
        faculites=request.env['placement.portal.users.data'].sudo().search([])
        faculites = faculites.filtered(lambda c: c.types == 'Faculty')
        filter = {'department': []}
        for faculty in faculites:
            not faculty.department in filter.get("department") and filter.get("department").append(faculty.department)
        return request.render("placement_portal.viewfacultylist",{'faculites': faculites, 'department': filter.get('department')})  

    @http.route(['/register'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def register(self, **post):
        if post:
            if post.get('password')==post.get('confirmpassword'):
                user=request.env['placement.portal.user.login'].sudo().create({
                    'email' : post.get('email'),
                    'password' : post.get('password'),
                    'types' : 'Student',
                    })
                request.env['placement.portal.users.data'].sudo().create({
                    'name' :post.get('name'),
                    'email' : post.get('email'),
                    'department' : int(post.get('department')),
                    'pass_out_year' : datetime.strptime(post.get('pass_out_year'),'%Y-%M-%d').year,
                    'types' : 'Student',
                    'user_id' : user.id,
                    })  
                return request.render("placement_portal.login", {'success': True})
            return request.render("placement_portal.mainpage", {'fail': True})

    @http.route(['/inquiry'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def inquiry(self, **post):
        if post:
            self.inquiry_mail(post.get('name'), post.get('email'), post.get('msg'))
        return request.render("placement_portal.mainpage", {'msg': True})

    # Login Pages
    @http.route(['/login'], auth='public', methods=['POST','GET'], type="http", website=True, csrf=False)
    def login(self, **kw):
        if kw:
            user=request.env['placement.portal.user.login'].sudo().search([('email', '=', kw.get('email'))])
            if user:
                request.session['user_id']=user.id
                if user.password==kw.get('password'):
                    if user.types=="Admin":
                        return http.local_redirect('/home')

                    elif user.types=="Student":
                        return http.local_redirect('/sviewhome')

                    elif user.types=="Faculty":
                        return http.local_redirect('/fviewhome')
            return request.render("placement_portal.login", {'fail': True})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/logout'], auth='public', type="http", website=True)
    def logout(self, **kw):
        if request.session.get('user_id'):
            request.session['user_id'] = False
            return http.local_redirect('/login')
        
    @http.route(['/forgot'], auth='public', methods=['POST','GET'], type="http", website=True, csrf=False)
    def forgot(self, **kw):
        if kw:
            email=request.env['placement.portal.user.login'].sudo().search([('email', '=', kw.get('email'))])
            if email:
                self.send_mail(email)
                
                return http.local_redirect('/login')
        return request.render("placement_portal.forgot")   

    @http.route('/user/deactivate/<int:user>', auth='user', type="http")
    def user_deactivate(self, user=None, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id)])
        if user:
            user.user_id.sudo().write({
                'active' : False,
                })
            user.sudo().write({
                'active' : False,
                })
            return http.local_redirect('/login')     


    # Admin Pages
    @http.route(['/home'], auth='public', methods=['POST','GET'], type="http", website=True, csrf=False)
    def home(self, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            total_fac = request.env['placement.portal.users.data'].search_count([('types', '=', 'Faculty')])
            total_stu = request.env['placement.portal.users.data'].search_count([('types', '=', 'Student')])
            total_dpart = request.env['placement.portal.department.data'].search_count([])
            return request.render("placement_portal.index_main", {'total_fac' : total_fac, 'total_stu' : total_stu,'total_dpart' : total_dpart})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/change'], methods=['POST','GET'], type="http", website=True, csrf=False)
    def change(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            if post:
                if user.user_id.password==post.get('old_pwd') and post.get('new_pwd')==post.get('con_pwd'):    
                    user.user_id.sudo().write({
                        'password' :post.get('new_pwd')
                        })
                    return http.local_redirect('/home')
                return request.render("placement_portal.change", {'fail': True})
            return request.render("placement_portal.change", {'fail': False})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/userform'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def userform(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            if post:
                user = request.env['placement.portal.user.login'].sudo().create({
                    'email' : post.get('email'),
                    'password' : post.get('password'),
                    'types' : post.get('types'),
                    })
                request.env['placement.portal.users.data'].sudo().create({
                    'name' :post.get('name'),
                    'email' : post.get('email'),
                    'pass_out_year' : datetime.strptime(post.get('pass_out_year'),'%Y-%M-%d').year,
                    'department' : int(post.get('department')),
                    'types' : post.get('types'),
                    'user_id' : user.id,
                    })
                if post.get('types')=='Faculty':
                    return http.local_redirect('/factdata')
                return http.local_redirect('/studentdata')

            departments=request.env['placement.portal.department.data'].sudo().search([])
            return request.render("placement_portal.userform", {'departments': departments})
        return request.render("placement_portal.login", {'fail': False})

    @http.route('/user/remove/<int:user>', auth='user', type="http")
    def user_remove(self, user=None, **kw):
        user=request.env['placement.portal.users.data'].sudo().browse([user])
        if user:
            user.user_id.sudo().write({
                'active' : False,
                })
            user.sudo().write({
                'active' : False,
                })
            if user.types=='Faculty':
                return http.local_redirect('/factdata')
            return http.local_redirect('/studentdata')

    @http.route(['/factdata'], auth='public', type="http", website=True)
    def factdata(self, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            faculites=request.env['placement.portal.users.data'].sudo().search([])
            faculites = faculites.filtered(lambda c: c.types == 'Faculty')
            return request.render("placement_portal.faculites",{'faculites': faculites} )
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/studentdata'], auth='public', type="http", website=True)
    def studentdata(self, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            students=request.env['placement.portal.users.data'].sudo().search([])
            students = students.filtered(lambda c: c.types == 'Student')
            return request.render("placement_portal.students",{'students': students} )
        return request.render("placement_portal.login", {'fail': False})
        
    @http.route(['/departdata'], auth='public', type="http", website=True)
    def departdata(self, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            departments=request.env['placement.portal.department.data'].sudo().search([])
            total_fac = request.env['placement.portal.users.data'].search_count([('types', '=', 'Faculty')])
            total_stu = request.env['placement.portal.users.data'].search_count([('types', '=', 'Student')])
            return request.render("placement_portal.department",{'departments': departments, 'total_fac' : total_fac, 'total_stu' : total_stu})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/departform'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def departform(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            if post:
                request.env['placement.portal.department.data'].sudo().create({
                    'name' : post.get('name'),
                    'code' : post.get('code'),
                    })              
                return http.local_redirect('/departdata')
            return request.render("placement_portal.departform")
        return request.render("placement_portal.login", {'fail': False})
    
    @http.route('/department/remove/<int:department>', auth='user', type="http")
    def department_remove(self, department=None, **kw):
        department=request.env['placement.portal.department.data'].sudo().browse([department])
        if department:
            department.unlink()
        return http.local_redirect('/departdata')

    @http.route(['/deactive'], auth='public', type="http", website=True)
    def deactive(self, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Admin')])
        if user:
            deactivated=request.env['placement.portal.users.data'].sudo().with_context(active=False).search([('active', '!=', True)])
            return request.render("placement_portal.deactive",{'deactivated': deactivated} )
        return request.render("placement_portal.login", {'fail': False})
    
    @http.route('/user/active/<int:user>', auth='user', type="http")
    def user_active(self, user=None, **kw):
        user=request.env['placement.portal.users.data'].sudo().with_context(active=False).browse([user])
        if user:
            user.user_id.sudo().with_context(active=False).write({
                'active' : True,
                })
            user.sudo().with_context(active=False).write({
                'active' : True,
                })
            return http.local_redirect('/deactive')

    # Faculity View Pages
    @http.route(['/fviewhome'], auth='public', type="http", website=True)
    def fviewhome(self, user=None, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Faculty')])
        if user:
            return request.render("placement_portal.fviewhome", {'user': user})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/fviewedit'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def fviewedit(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Faculty')])
        if user:
            if post:
                values={
                    'name' :post.get('name'),
                    'dob' : post.get('dob'),
                    'education' : post.get('education'),
                    'location' : post.get('location'),
                    'skills' : post.get('skills'),
                    'facebook' : post.get('facebook'),
                    'instagram' : post.get('instagram'),
                    'linkedin' : post.get('linkedin'),
                    }
                if post.get('img'):
                    values.update({'img' : base64.b64encode(post.get('img').read())})
                user.sudo().write(values)
                return http.local_redirect('fviewhome')
            return request.render("placement_portal.fviewedit", {'user': user})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/fviewchange'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def fviewchange(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Faculty')])
        if user:
            if post:
                if user.user_id.password==post.get('old_pwd') and post.get('new_pwd')==post.get('con_pwd'):    
                    user.user_id.sudo().write({
                        'password' :post.get('new_pwd')
                        })
                    return http.local_redirect('fviewhome')
                return request.render("placement_portal.fviewchange", {'fail': True})  
            return request.render("placement_portal.fviewchange", {'fail': False})  
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/fviewuseradd'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def fviewuseradd(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Faculty')])
        if user:
            if post:    
                user=request.env['placement.portal.user.login'].sudo().create({
                    'email' : post.get('email'),
                    'password' : post.get('password'),
                    'types' : 'Student',
                    })
                request.env['placement.portal.users.data'].sudo().create({
                    'name' :post.get('name'),
                    'email' : post.get('email'),
                    'department' : int(post.get('department')),
                    'pass_out_year' : datetime.strptime(post.get('pass_out_year'),'%Y-%M-%d').year,
                    'types' : 'Student',
                    'user_id' : user.id,
                    })  
                return http.local_redirect('/fviewstudentdata')

            departments=request.env['placement.portal.department.data'].sudo().search([])
            return request.render("placement_portal.fviewuseradd", {'departments': departments})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/fviewstudentdata'], auth='public', type="http", website=True)
    def fviewstudentdata(self, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Faculty')])
        if user:
            students=request.env['placement.portal.users.data'].sudo().search([])
            students = students.filtered(lambda c: c.types == 'Student')
            return request.render("placement_portal.fviewstudentdata",{'students': students} )
        return request.render("placement_portal.login", {'fail': False})

    # Student View Pages
    @http.route(['/sviewhome'], auth='public', type="http", website=True)
    def sviewhome(self, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Student')])
        if user:
            timelines=user.timeline_ids
            # timelines=user.timeline_ids.sudo().search([('user_id.id', '=', request.session.user_id)],order="start_date desc")
            return request.render("placement_portal.sviewhome", {'user': user, 'timelines' : timelines})
        return request.render("placement_portal.login", {'fail': False})

    @http.route('/user/timeline/<int:timeline>', methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def user_timeline(self, timeline=None, **kw):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Student')])
        if user:
            timelines=user.timeline_ids.sudo().browse([timeline])
            if timelines and kw:    
                values={
                        'job_des' : kw.get('job_des'),
                        }
                if kw.get('end_date'):
                    values.update({'end_date' : kw.get('end_date')})
                    
                timelines.sudo().write(values)
                return http.local_redirect('/sviewhome')

    @http.route(['/sviewedit'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def sviewedit(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Student')])
        if user:
            if post:
                values={
                    'name' :post.get('name'),
                    'dob' : post.get('dob'),
                    'education' : post.get('education'),
                    'location' : post.get('location'),
                    'skills' : post.get('skills'),
                    'facebook' : post.get('facebook'),
                    'instagram' : post.get('instagram'),
                    'linkedin' : post.get('linkedin'),
                    }
                if post.get('img'):
                    values.update({'img' : base64.b64encode(post.get('img').read())})
                user.sudo().write(values)
                return http.local_redirect('sviewhome')
            return request.render("placement_portal.sviewedit", {'user': user})
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/add/timeline'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def addtimeline(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Student')])
        if user:
            if post:
                values={
                    'cname' : post.get('cname'),
                    'job_des' : post.get('job_des'),
                    'start_date' : post.get('start_date'),
                    'user_id' : user.id
                    }
                if post.get('end_date'):
                    values.update({'end_date' : post.get('end_date')})
                
                request.env['placement.portal.time.line'].sudo().create(values)
            return http.local_redirect('/sviewhome')
        return request.render("placement_portal.login", {'fail': False})

    @http.route(['/sviewchange'], methods=['POST','GET'], auth='public', type="http", website=True, csrf=False)
    def sviewchange(self, **post):
        user=request.env['placement.portal.users.data'].sudo().search([('user_id.id', '=', request.session.user_id),('types', '=',  'Student')])
        if user:
            if post:
                if user.user_id.password==post.get('old_pwd') and post.get('new_pwd')==post.get('con_pwd'):    
                    user.user_id.sudo().write({
                        'password' :post.get('new_pwd')
                        })
                    return http.local_redirect('/sviewhome')
                return request.render("placement_portal.sviewchange", {'fail': True}) 
            return request.render("placement_portal.sviewchange", {'fail': False})     
        return request.render("placement_portal.login", {'fail': False})

    def send_mail(self, email):
        import smtplib
        message = 'Subject: {}\n\n{}'.format("no_reply", "Your Password is :"+str(email.password))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("charulpatel241099@gmail.com", "cp@2499#love")
        server.sendmail("charulpatel241099@gmail.com", email.email, message)
        # server.sendmail("charulpatel241099@gmail.com", email.email, "Your Password is " + str(email.password))
        server.quit()

    def inquiry_mail(self, name,email,msg):
        import smtplib
        message = 'Subject: {}\n\n{}'.format("inquiry_mail: "+str(email),"\n"+str(name)+"\n\n"+str(msg))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("charulpatel241099@gmail.com", "cp@2499#love")
        server.sendmail("charulpatel241099@gmail.com", "charulpatel241099@gmail.com", message)
        server.quit()