##########################################
# 后续处理函数
##########################################
import re
import csv
#用于替换value字段内的奇怪字符
VALUE_REPLACE_CHARS = '[📮]'
def reject_bad_chars_of_value(src_string, badchars=VALUE_REPLACE_CHARS):
    result = re.sub(badchars, "", src_string)
    return result
#print(reject_bad_chars("邮筒📮"))

#用于去除错误邮编
REGULAR_POSTCODE =re.compile(r'^[0-9]{6}$')
def is_postcode(src_postcode, regular_postcode=REGULAR_POSTCODE):
    postcode = re.search(regular_postcode, src_postcode)
    if postcode:
        return True
    else:
        return False
#print(is_postcode('12345 '))

#用于规范电话的格式
#如果校验通过，返回正确格式的电话，否则返回空字符串
REGULER_PHONE = re.compile(r'^(86)?(021|21)?([0-9]{8}|[0-9]{11}|400[0-9]{7}|[0-9]{5})$')
def audit_phone(src_phone, regular_phone=REGULER_PHONE):
    new_phone = re.sub(r'[+ \-()]', '', src_phone)
    phone = re.search(regular_phone, new_phone)
    if phone:
        phone_num = phone.group(3)
        phone_type = len(phone_num)
        #固话
        if phone_type==8:
            return '+86-021-' + phone_num
        #手机
        elif phone_type==11:
            return '+86-' + phone_num
        #400电话
        elif phone_type==10:
            return '+86-' + phone_num
        #全国通用电话
        elif phone_type==5:
            return '+86-' + phone_num
        else:
            return ''
    else:
        return ''
#test_phone = ['4008123123','862122163900','+86 6361 2898','021-63914848, 021-63522222','+86 21 38809988','2164312091','86-21-50559888','+2147483647','+862164712821','+18 13621675140','02162883030','+86-21-5160-7888','+86 138 1609 3747','(021) 3356-3996','021-63779282','+86 (0)21-68778787']
#for phone in test_phone:
#    print(audit_phone(phone))

#读取CSV文件并检查
def audit_tag_files(file_name):
    file_data = []
    
    with open(file_name, "r", encoding='utf-8') as f:
        reader= csv.DictReader(f)
        
        for row in reader:
            #去除坏字符
            row['value'] = reject_bad_chars_of_value(row['value'])
            #规范电话格式
            if row['key']=='phone':
                tmp_phone = audit_phone(row['value'])
                if tmp_phone!='':
                    row['value'] = tmp_phone
                    file_data.append(row)
                else:
                    print('错误的电话格式' + str(row))
            #去除错误的邮编
            elif row['key']=='postcode':
                if is_postcode(row['value']):
                    file_data.append(row)
                else:
                    print('错误的邮编格式' + str(row))
            #其他情况默认保留
            else:
                file_data.append(row)
                
    return file_data

# 写文件函数
FIELD_NAMES=['id','key','value','type']
def write_csv_file(file_name, file_data, field_names=FIELD_NAMES):
    with open(file_name, "w", encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, delimiter=",", fieldnames=field_names)
        writer.writeheader()
        for row in file_data:
            writer.writerow(row)
        print('完成: ' + file_name + "文件写入.")

#CSV文件检查并生成新文件的入口函数
def check_and_write_new_csv_file(src_file_name):
    file_data = audit_tag_files(src_file_name)
    new_file_name = src_file_name.split('.')[0] + '_new.csv'
    write_csv_file(new_file_name, file_data)
	
check_and_write_new_csv_file('nodes_tags.csv')
check_and_write_new_csv_file('ways_tags.csv')
check_and_write_new_csv_file('rel_tags.csv')