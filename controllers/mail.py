# import csv, smtplib, ssl


# def sendmail(email,password):
#     message = """Your :""" 
#     from_address = "charulpatel241099@gmail.com"
#     password = "cp@2499#love"

#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#         server.login(from_address, password)
#         server.sendmail(
#             from_address,
#             email,
#             message,
#         )
        
# def sendmain(email, password)
#     template_obj = self.env['mail.mail']
#     template_data = {
#                     'subject': 'Due Invoice Notification : ' + current_date,
#                     'body_html': message_body,
#                     'email_from': sender,
#                     'email_to': ", ".join(recipients)
#                     }
#     template_id = template_obj.create(template_data)
#     template_obj.send(template_id)