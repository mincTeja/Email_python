import imaplib,email,os,json,sys,time
from optparse import OptionParser

def write_file(attachment_info_d):
    with open('./download_info/info.json', 'w+') as file:
        file.write(json.dumps(attachment_info_d)) 

def read_file():
    with open('./download_info/info.json','r+') as file:
        try:
            d=json.load(file)
            return d
        except:
            return {}


def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None,True)

def get_attachments(msg):
    
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            #print("multipart")
            continue
        if part.get('Content-Disposition') is None:
            #print("disposition")
            continue
        filename=part.get_filename()
        print(filename)
        if bool(filename):
            filePath= os.path.join(attachment_dir,filename)
            with open(filePath,'wb') as f:
                f.write(part.get_payload(decode=True))
        print("done")



def search(key,value,con):
    _,data=con.search(None,key,'"{}"'.format(value))
    print(data)
    print(list(data))
    return data

def get_emails(result_bytes):
    msgs=[]
    for n in result_bytes: #[0].split():
        _,data=con.fetch(n,('RFC822'))
        msgs.append(data)
    return msgs

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-u","--username",dest="username",help="Username")
    parser.add_option("-p","--password",dest="password",help="App specific password")
    parser.add_option("-f","--from",dest="from_email",help="Senders email whose attachment needs to be retrieved")
    options,args=parser.parse_args()
    
    d=read_file()
    #print(d)
    try:
        user= options.username 
        password= options.password 
        host='imap.gmail.com'
        from_email=options.from_email
        attachment_dir= './attachments/' + time.strftime("%d%m%Y")
        con=imaplib.IMAP4_SSL(host)
        con.login(user,password)

    except:
        print("Please provide all the options.\nfor help execute python3 read.py -h")
        sys.exit(1)
    try:
        os.mkdir(attachment_dir)
    except:
        print('directory already exists')

    
    con.select('INBOX')

    # result,data=con.fetch(b'1068','(RFC822)')
    # row=email.message_from_bytes(data[0][1])
    # print(get_body(row))
    # get_attachments(row)

    b_check=0
    if from_email in d.keys():
        b_check=int(d[from_email])
    print(b_check)
    op1=search('FROM',from_email,con)
    
    op2=get_emails(list(filter(lambda x:int(x.decode('utf-8'))>b_check,op1[0].split())))

    try:
        for i in op2:
            row=email.message_from_bytes(i[0][1])
            print(get_body(row))
            get_attachments(row)
    except Exception as e:
        print(e)
        sys.exit(1)
    d[from_email]= str(op1[0].split()[-1],'utf-8') 
    write_file(d)
    x=read_file()
    print(x)
    con.close()
    con.logout()