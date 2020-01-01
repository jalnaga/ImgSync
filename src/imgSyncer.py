'''
Copy images from the dropbox image forlder to the user's picture folder.

Copied images are most recent images since modified.
Add some random images for the variety of update.
Random images are updated daily.

There are 2 types of images.
    1. Normal images
    2. Hentai images

- Total number of images is set by maxImgNum.
- The ratio between hentai images and normal images is set by hentaiImgRatio.
    - ex) If the total number of image is 10 and henati image ratio is 0.25,
        then normal images are 6 and hentai images are 4.(10*0.25)
- Each types have some random images from each types.
    - Its ratio is set by randomImgRatio
'''
import sys
import os
from shutil import copy2
import glob

import random
from configparser import ConfigParser


class ImgNum(object):
    def __init__(self, maxNum=20, randomRatio=0.2, **categoryRatios):
        super(ImgNum, self).__init__()
        self.maxNum = maxNum
        self.rRatio = randomRatio
        self.catRatios = self.normalize_ratio(*list(categoryRatios.values()))
        self.nums = self.gen_num()

    def normalize_ratio(self, *ratios):
        self.catRatios = []
        sumCatRatio = sum(ratios)
        for ratio in ratios:
            normRat = ratio * 1.0/sumCatRatio
            self.catRatios.append(normRat)
        return self.catRatios

    def gen_num(self):
        self.nums = []
        for ratio in self.catRatios:
            num = int(self.maxNum*ratio)
            rNum = int(num*self.rRatio)
            num = num - rNum
            self.nums.append((num, rNum))
        return self.nums


class Images(object):
    def __init__(self, folder, nums=(1, 0)):
        super(Images, self).__init__()
        self.nums = nums
        self.folder = folder
        self.sortStatus = False
        self.files = self.get_all_imgs()
        self.randoms = self.get_random_imgs()
        self.imgs = []

    def is_valid(self):
        return (os.path.isdir(self.folder) and os.path.exists(self.folder))

    def get_all_imgs(self):
        if self.is_valid():
            self.files = []
            for r, d, f, in os.walk(self.folder):
                for file in f:
                    if '.ini' not in file:
                        self.files.append(os.path.join(r, file))
            self.sortStatus = False
        return self.files

    def get_random_imgs(self):
        self.randoms = []
        if len(self.files) > 0:
            self.randoms = random.sample(self.files, k=self.nums[1])
        return self.randoms

    def sort_by_mtime(self):
        if len(self.files) > 0 and self.sortStatus == False:
            self.files.sort(key=lambda img: os.stat(
                img).st_mtime, reverse=True)
            self.sortStatus = True
        return self.files

    def get_imgs(self):
        if 0 <= self.nums[0] < len(self.files):
            self.imgs = self.files[:self.nums[0]] + self.randoms
            self.imgs = list(set(self.imgs))
        return self.imgs


class IniSet(object):
    def __init__(self, file=''):
        super(IniSet, self).__init__()
        self.file = file
        self.cfg = ConfigParser()
        self.targetFolder = 'C:\\Users\\jalnaga\\Pictures'
        self.nonHentaiFolder = 'D:\\Dropbox\\Image\\Images\\Images'
        self.hentaiFolder = 'D:\\Dropbox\\Image\\Images18X\\Images18X'
        self.maxNum = 10
        self.randomRatio = 0.2
        self.nonHentaiRatio = 0.7
        self.hentaiRatio = 0.3
        self.prevNonHentaiImgNum = 0
        self.prevHentaiImgNum = 0
        self.nonHentaiRandomImgs = []
        self.hentaiRandomImgs = []
        if self.is_valid():
            self.load_ini()
        else:
            self.save_ini()

    def save_ini(self):
        self.cfg['Folder'] = {'Target Folder': self.targetFolder,
                              'Non Hentai Folder': self.nonHentaiFolder,
                              'Hentai Folder': self.hentaiFolder}
        self.cfg['Number'] = {'Maximum Number': str(self.maxNum),
                              'Random Ratio': str(self.randomRatio), 'Non Hentai Ratio': str(self.nonHentaiRatio),
                              'Hentai Ratio': str(self.hentaiRatio)}
        self.cfg['Update'] = {'Previous Non hentai images number': str(self.prevNonHentaiImgNum),
                              'Previous Hentai images number': str(self.prevHentaiImgNum)}
        self.cfg['NonHentaiRandomImgs'] = {i: self.nonHentaiRandomImgs[i]
                                           for i in range(0, len(self.nonHentaiRandomImgs))}
        self.cfg['HentaiRandomImgs'] = {i: self.hentaiRandomImgs[i]
                                        for i in range(0, len(self.hentaiRandomImgs))}
        with open(self.file, 'w') as configFile:
            self.cfg.write(configFile)

    def load_ini(self):
        if self.is_valid():
            self.cfg.read(self.file)
            self.targetFolder = self.cfg['Folder']['Target Folder']
            self.nonHentaiFolder = self.cfg['Folder']['Non Hentai Folder']
            self.hentaiFolder = self.cfg['Folder']['Hentai Folder']
            self.maxNum = int(self.cfg['Number']['Maximum Number'])
            self.randomRatio = float(self.cfg['Number']['Random Ratio'])
            self.nonHentaiRatio = float(self.cfg['Number']['Non Hentai Ratio'])
            self.hentaiRatio = float(self.cfg['Number']['Hentai Ratio'])
            self.prevNonHentaiImgNum = int(
                self.cfg['Update']['Previous Non hentai images number'])
            self.prevHentaiImgNum = int(
                self.cfg['Update']['Previous Hentai images number'])
            self.nonHentaiRandomImgs = list(
                self.cfg['NonHentaiRandomImgs'].values())
            self.hentaiRandomImgs = list(self.cfg['HentaiRandomImgs'].values())

    def is_valid(self):
        return os.path.exists(self.file)


if __name__ == "__main__":
    filePath = (os.path.dirname(os.path.realpath(__file__)))
    iniFileName = os.path.join(filePath, 'imgSync.ini')

    iniFile = IniSet(file=iniFileName)

    imgNum = ImgNum(maxNum=iniFile.maxNum, randomRatio=iniFile.randomRatio,
                    nonHenati=iniFile.nonHentaiRatio, hentai=iniFile.hentaiRatio)

    targetImgs = Images(iniFile.targetFolder)
    nonHentaiImgs = Images(
        iniFile.nonHentaiFolder, nums=imgNum.nums[0])
    hentaiImgs = Images(
        iniFile.hentaiFolder, nums=imgNum.nums[1])

    def remove_old_randImgs_in_target(imgs):
        for f in imgs:
            fileInTarget = os.path.join(
                targetImgs.folder, os.path.basename(f))
            if os.path.exists(fileInTarget):
                os.remove(fileInTarget)

    updateRequired = False

    if targetImgs.is_valid() and len(nonHentaiImgs.files) > 0 and len(hentaiImgs.files) > 0:
        if iniFile.prevNonHentaiImgNum == len(nonHentaiImgs.files) and iniFile.prevHentaiImgNum == len(hentaiImgs.files):
            updateRequired = False
        else:
            updateRequired = True
        
        if len(targetImgs.files) != imgNum.maxNum:
            updateRequired = True

        if updateRequired:
            for f in targetImgs.files:
                if os.path.exists(f):
                    os.remove(f)
            nonHentaiImgs.sort_by_mtime()
            hentaiImgs.sort_by_mtime()
            nonHentaiImgs.get_imgs()
            hentaiImgs.get_imgs()
            iniFile.nonHentaiRandomImgs = nonHentaiImgs.randoms
            iniFile.hentaiRandomImgs = hentaiImgs.randoms
            iniFile.prevNonHentaiImgNum = len(nonHentaiImgs.files)
            iniFile.prevHentaiImgNum = len(hentaiImgs.files)
            for f in nonHentaiImgs.imgs:
                copy2(f, targetImgs.folder)
            for f in hentaiImgs.imgs:
                copy2(f, targetImgs.folder)
            
            print('Fully Updated!')
        else:
            remove_old_randImgs_in_target(iniFile.nonHentaiRandomImgs)
            remove_old_randImgs_in_target(iniFile.hentaiRandomImgs)
            iniFile.nonHentaiRandomImgs = nonHentaiImgs.get_random_imgs()
            iniFile.hentaiRandomImgs = hentaiImgs.get_random_imgs()
            for f in iniFile.nonHentaiRandomImgs:
                copy2(f, targetImgs.folder)
            for f in iniFile.hentaiRandomImgs:
                copy2(f, targetImgs.folder)
            
            print('Partial Updated!')
        iniFile.save_ini()
    else:
        print('***Error: There is no image folder.')
        sys.exit()
