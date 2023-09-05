import xml.etree.ElementTree as ElementTree
import tarfile
import shutil
import glob
import os
import re



def clean_text(answertext):
    out_text=answertext
    out_text = out_text.replace('&lt;','<').replace('&gt;','>').replace('&amp;lt;','<').replace('&amp;gt;','>')
    out_text = re.sub(re.compile(r'<[^>]+>'), ' ', out_text)
    out_text = re.sub(re.compile(r"\s+"), ' ', out_text).strip()

    return out_text


def print_q(q, text):
    if q.find('qtype').text == 'match':
        for answer in q.findall('plugin_qtype_match_question/matches/match'):
            text = "{}    {}   <=>   {}\n".format(text,
                                                  clean_text(answer.find('answertext').text),
                                                  answer.find('answertext').text)

    if q.find('qtype').text == 'essay':
        text = "{}    {}\n".format(text, "!!! Потрібно дати текстову відповідь !!!")

    if q.find('qtype').text == 'multichoice':
        for answer in q.findall('plugin_qtype_multichoice_question/answers/answer'):
            text = "{}    {} ({})\n".format(text, clean_text(answer.find('answertext').text),
                                            float(answer.find('fraction').text))

    if q.find('qtype').text == 'gapselect':
        for answer in q.findall('plugin_qtype_gapselect_question/answers/answer'):
            text = "{}    {} ({} хз як дізнатись правильну відповідь)\n".format(text, clean_text(
                answer.find('answertext').text),
                                                                                float(answer.find('fraction').text))

    if q.find('qtype').text == 'shortanswer':
        for answer in q.findall('plugin_qtype_shortanswer_question/answers/answer'):
            text = "{}    {} ({})\n".format(text,
                                            clean_text(answer.find('answertext').text),
                                            float(answer.find('fraction').text))

    if q.find('qtype').text == 'truefalse':
        for answer in q.findall('plugin_qtype_truefalse_question/answers/answer'):
            text = "{}    {} ({})\n".format(text, clean_text(answer.find('answertext').text),
                                            float(answer.find('fraction').text))

    return text




for archive in glob.glob("./**.mbz", recursive=True):
    print('{} : '.format(archive))
    out_folder = 'tmp/{}'.format(archive.replace('.mbz', ''))
    file = tarfile.open(archive)
    file.extractall(out_folder)
    file.close()
    out_dir = "{} {}".format(
        ElementTree.parse("{}/moodle_backup.xml".format(out_folder)).getroot() \
        .find('information/original_course_id').text,
        ElementTree.parse("{}/moodle_backup.xml".format(out_folder)).getroot() \
                        .find('information/original_course_fullname').text
                        )

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for child in ElementTree.parse("{}/files.xml".format(out_folder)).getroot():
        src_name = child.find('contenthash').text
        ext_name = child.find('filename').text

        if ext_name != '.':
            files = glob.glob("{}/files/**/{}".format(out_folder, src_name), recursive=True)
            shutil.copyfile(files[0], '{}/{}'.format(out_dir, ext_name))
            print('   {} +'.format(ext_name))

    for child in ElementTree.parse("{}/moodle_backup.xml".format(out_folder))\
            .getroot().\
            findall('information/contents/activities/activity'):
        if child.find('modulename').text == 'page':
            ext_name = '{}.html'.format(child.find('title').text)
            directory = '{}/{}/page.xml'.format(out_folder, child.find('directory').text)
            doc_root = ElementTree.parse(directory).getroot().find('page')

            with open('{}/{}'.format(out_dir,ext_name), 'w', encoding="utf-8") as f:
                f.write('<html>')
                f.write('<head>')
                f.write('<title>')
                f.write(doc_root.find('name').text)
                f.write('</title>')
                f.write('</head>')
                f.write('<body>')
                f.write('<h1>')
                f.write(doc_root.find('name').text)
                f.write('</h1>')
                f.write(doc_root.find('content').text)
                f.write('</body>')
                f.write('</html>')
                f.close()
            print('   {} +'.format(ext_name))

    quest = []

    for question_category in ElementTree.parse("{}/questions.xml".format(out_folder)) \
            .getroot(). \
            findall('question_category'):
        for question in question_category.findall('questions/question'):
            quest.append(question)



    for child in ElementTree.parse("{}/moodle_backup.xml".format(out_folder)).getroot() \
            .findall('information/contents/activities/activity'):
        if child.find('modulename').text == 'quiz':
            directory = '{}/{}'.format(out_folder, child.find('directory').text)

            text = '{}\n\n'.format(child.find('title').text)

            for quiz in ElementTree.parse("{}/quiz.xml".format(directory)).getroot().findall(
                    'quiz/question_instances/question_instance'):
                for q in quest:
                    if quiz.find('questionid').text == q.attrib.get('id'):
                        text = '{}\n{} {}\n'.format(text, q.find('name').text,
                                        clean_text(q.find('questiontext').text))

                        text = print_q(q, text)

            with open('{}/{}.txt'.format(out_dir, child.find('title').text), 'w') as f:
                f.write(text)

    text=''
    for q in quest:
        text = '{}\n{} {}\n'.format(text, q.find('name').text, clean_text(q.find('questiontext').text))
        text = print_q(q, text)

    with open('{}/{}_all.txt'.format(out_dir, out_dir), 'w') as f:
                f.write(text)

    shutil.rmtree('tmp')
