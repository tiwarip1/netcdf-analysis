import os
import shutil

def sorting():
    directory = '../Lingyun-data/'

    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if 'Copy' in file]

    if not os.path.exists('{}extras/'.format(directory)):
        os.makedirs('{}extras/'.format(directory))

    for file in filtered_files:
        
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)

    filtered_files = [file for file in files_in_directory]

    for file in filtered_files:

        if file[-2:]!='nc':

            shutil.move('{}{}'.format(directory,file),'{}extras/{}'.format(directory,file))

