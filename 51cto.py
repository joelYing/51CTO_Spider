#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5

import os
import re
import requests

# 存在缺点：长时间的爬取，可能会中断访问，但是再启动之后可以接着爬取之后的内容（算解决一半，问题不大）


class CTO(object):
    def __init__(self):
        self.file_path = 'D:\\Python\\PycharmProject\\CTO\\{}'
        self.train_url = 'http://edu.51cto.com/center/wejob/user/train-course-ajax?train_id=104&page=1&size=20'
        self.course_url = 'http://edu.51cto.com/center/wejob/user/course-info-ajax?&train_course_id={}&page={}&size=20'
        self.lesson_info = 'http://edu.51cto.com/center/player/play/get-lesson-info?type=wejoboutcourse&sign=...&lesson_id={}_{}'
        # 注意可能需要更新cookies，加上u-a或accept
        self.cookie = {
            'Cookie':'_51ctologStr=your-cookies' # 可能需要会员
        }

    @staticmethod
    def tool(text):
        pattern = re.compile(r'\[|]')
        text = re.sub(pattern, '', text)
        return text

    def gethtml(self):
        s = requests.session()
        # 5大节课程
        r_train = s.get(self.train_url, cookies=self.cookie)
        train = r_train.json()
        infos = train['data']['data']
        for info in infos:
            # print(info) 每一个大课程
            lesson_num = info['lesson_num']
            file_num = info['sort']  # 课程编号
            # 已进行到第三块课程
            if int(file_num) > 2:
                file_url = 'http://edu.51cto.com' + info['list_url']
                train_course_id = info['train_course_id']  # 课程的id 如221
                print(train_course_id)
                path = self.file_path.format(file_num)  # 根据课程数创建对应的课程文件夹
                f = os.path.exists(path)
                if not f:
                    os.makedirs(path)
                    print('make file success...')
                else:
                    print('file already exists...')
                pages = int(lesson_num / 20) + 1  # 每个课程的课时页数
                for page in range(1, pages + 1):
                    # 每一页
                    print(page)
                    r_list = s.get(self.course_url.format(str(train_course_id), page), cookies=self.cookie)
                    lesson_info_list = re.findall(r'"lesson_id":"(.*?)".*?"lesson_name":"(.*?)"', r_list.text, re.S)
                    # 每一页对应的存在的课程视频的id
                    for lesson_info in lesson_info_list:
                        lesson_id, lesson_name = lesson_info[0], lesson_info[1]
                        lesson_name = lesson_name.encode('utf-8').decode('unicode-escape')
                        p = re.compile(' ')
                        lesson_name = p.sub('', lesson_name)
                        print(lesson_id, lesson_name)
                        path = 'D:\\Python\\PycharmProject\\CTO\\{}\\{}'.format(file_num, lesson_id)  # 每个视频创建一个视频id的文件夹
                        f = os.path.exists(path)
                        # 基于中断后，创建文件时判断，若存在该文件夹则跳过对该视频的下载，若不存在则继续
                        if not f:
                            os.makedirs(path)
                            print('2 make file success...')
                            # 获取对应id的视频的ajax返回
                            r_lesson = s.get(self.lesson_info.format(str(train_course_id), str(lesson_id)),
                                             cookies=self.cookie)
                            if r_lesson.text == 'video_id_error':
                                print(u'作业...')
                            else:
                                rj = r_lesson.json()
                                res = s.get(rj['dispatch_list'][0]['value'][0]['url'], cookies=self.cookie)
                                # print(res.text)
                                # 保存对应的m3u8文件
                                # with open('D:\\Python\\PycharmProject\\CTO\\{}\\{}\\{}.txt'.format(file_num, lesson_id, rj['lesson_title']), 'w') as f:
                                #     f.write(res.text)
                                # with open('D:\\Python\\PycharmProject\\CTO\\{}\\{}\\{}.txt'.format(file_num, lesson_id, rj['lesson_title']), 'r') as f:
                                #     text = f.read()
                                # print(text)
                                fand_url = re.findall(r'https:(.*?)\.ts', res.text, re.S)
                                nums = len(fand_url)
                                # for ts_url in fand_url:
                                for num in range(1, nums + 1):
                                    short_url = 'https:' + fand_url[num - 1] + '.ts'
                                    print(short_url)
                                    # sname = re.findall(r'//.*?51cto.com/\?p=.*?&sname=(.*?)\.ts', str(short_url), re.S)[0]
                                    res_ts = s.get(short_url, cookies=self.cookie)
                                    b_num = num
                                    if num < 10:
                                        b_num = '00' + str(num)
                                    if 9 < num < 100:
                                        b_num = '0' + str(num)
                                    with open('D:\\Python\\PycharmProject\\CTO\\{}\\{}\\{}.ts'.format(file_num, lesson_id, b_num), 'wb') as f:
                                        f.write(res_ts.content)
                                        print('OK')
                                os.system('copy /b D:\\Python\\PycharmProject\\CTO\\{}\\{}\\*.ts  D:\\Python\\PycharmProject\\FinalCTO\\{}\\{}.mp4'.format(file_num, lesson_id, file_num, lesson_name))
                        else:
                            print('2 file already exists...')
            else:
                print(u'课程大类已处理')
            # break


if __name__ == '__main__':
    cto = CTO()
    cto.gethtml()
