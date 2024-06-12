import requests
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher

# تابع برای تمیز کردن نام فایل
def clean_file_name(url):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        url = url.replace(char, '_')
    return url

# تابع برای دریافت محتوای وب سایت
def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f'خطا در دریافت محتوای {url}: {e}')
        return None

# تابع برای ارسال ایمیل
def send_email(subject, body, to_email, email_config):
    msg = MIMEMultipart()
    msg['From'] = email_config['from_email']
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
    server.starttls()
    server.login(email_config['from_email'], email_config['password'])
    text = msg.as_string()
    server.sendmail(email_config['from_email'], to_email, text)
    server.quit()

# اصلی
def main():
    # دریافت ورودی‌ها از کاربر
    websites = input('لطفا لیست آدرس وب سایت‌ها را وارد کنید (جدا شده با کاما): ').split(',')
    interval_minutes = int(input('تعداد دقیقه برای چک کردن وب سایت‌ها را وارد کنید: '))
    save_path = input('محل ذخیره سازی فایل‌ها را وارد کنید: ')
    to_email = input('ایمیل برای ارسال هشدار را وارد کنید: ')
    match_percentage = float(input('درصد انطباق را وارد کنید: '))

    # تنظیمات ایمیل
    email_config = {
        'from_email': 'your_email@example.com',
        'password': 'your_password',
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587
    }

    last_content = {}
    while True:
        for url in websites:
            content = get_website_content(url)
            if content:
                # ذخیره محتوای وب سایت
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                clean_url = clean_file_name(url)
                file_name = f'{clean_url}_{timestamp}.html'
                file_path = f'{save_path}/{file_name}'
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

                # مقایسه محتوای جدید با آخرین محتوا و ایجاد لاگ
                log_content = ''
                if url in last_content and content != last_content[url]:
                    similarity = SequenceMatcher(None, content, last_content[url]).ratio() * 100
                    log_content += f'میزان انطباق: {similarity:.2f}%\n'
                    # تعیین عنوان ایمیل بر اساس میزان تغییرات
                    if similarity < match_percentage:
                        subject = 'لاگ'
                    else:
                        subject = 'ارسال لاگ'
                    # ایجاد فایل لاگ
                    log_file_name = f'log_{clean_url}_{timestamp}.txt'
                    log_file_path = f'{save_path}/{log_file_name}'
                    with open(log_file_path, 'w', encoding='utf-8') as log_file:
                        log_file.write(log_content)
                    # ارسال ایمیل با لاگ
                    send_email(subject, log_content, to_email, email_config)

                last_content[url] = content
        time.sleep(interval_minutes * 60)

if __name__ == '__main__':
    main()
