import smtplib, ssl
import sys

SERVER = 'smtp.gmail.com'
PORT = 587
SENDER_EMAIL = "vidcrypt@gmail.com"
PASSWORD = "cryptvid92"

def send_email(from_address, password, to_address, host, port, msg_obj):
	subject = msg_obj['subject']
	msg_text = msg_obj['msg_text']

	msg = """Subject:{0}\n{1}""".format(subject, msg_text)

	try:
		server = smtplib.SMTP(host, port)
		server.starttls()
		server.login(from_address, password)

		server.sendmail(from_address, to_address, msg)
		
	except Exception as e:
		print(e)
		pass

	finally:
		server.quit()

if __name__ == '__main__':
	subject = sys.argv[1]
	msg = sys.argv[2]
	to = sys.argv[3]

	msg_obj = {"subject":subject, "msg_text": msg} 

	send_email(
		SENDER_EMAIL, PASSWORD, to,
		SERVER, PORT,  msg_obj
	)
