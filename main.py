import xml.etree.ElementTree as ElementTree
import tarfile
import shutil
import glob
import os

for archive in glob.glob("./**.mbz", recursive=True):
    print('{} : '.format(archive))
    out_folder = 'tmp/{}'.format(archive.replace('.mbz', ''))
    out_dir = archive.replace('.mbz', '')
    file = tarfile.open(archive)
    file.extractall(out_folder)
    file.close()

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

    shutil.rmtree('tmp')
