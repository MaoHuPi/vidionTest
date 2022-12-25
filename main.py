import pygame
import tkinter
import tkinter.filedialog
import mediapipe as mp
import numpy as np
import cv2
import random
import json
import time
import math
import os
DES = '''Developed by MaoHuPi
Copyright: 2022 © MaoHuPi
App Name: Vidion Test
Verstion: 1.0.0'''


path = '.' if os.path.isfile(
    './'+os.path.basename(__file__)) else os.path.dirname(os.path.abspath(__file__))

# basic method


def rad(deg): return deg/360*(math.pi*2)
def deg(rad): return rad/(math.pi*2)*360


def vectorVal(p1, p2):
    return (math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2)))


def vectorDeg(p1, p2):
    dX = (p2[0] - p1[0])
    dY = (p2[1] - p1[1])
    r = math.atan(dX/dY if dY != 0 else math.inf)
    d = deg(r)

    d = abs(d)
    # 45 0 45
    # 90   90
    # 45 0 45
    if dY < 0:
        d = 180 - d
    # 45   0   45
    # 90       90
    # 135 180 135
    if dX < 0:
        d = 360 - d
    # 315  0   45
    # 270      90
    # 225 180 135
    return (d)


def rectRelativePos(rect=(0, 0, 10, 10), p=(5, 5)):
    if type(rect) in [list, tuple]:
        class rect:
            x = rect[0]
            y = rect[1]
            w = rect[2]
            h = rect[3]
    if type(p) in [list, tuple]:
        class p:
            x = p[0]
            y = p[1]
    return ([(p.x - rect.x)/rect.w, (p.y - rect.y)/rect.h])


def inputFile():
    win_tk = tkinter.Tk()
    win_tk.withdraw()
    filePath = tkinter.filedialog.askopenfilename(parent=win_tk)
    win_tk.destroy()
    return filePath

# color


class color:
    WHITE = [255, 255, 255]
    BLACK = [0, 0, 0]
    RED = [255, 0, 0]
    GREEN = [0, 255, 0]
    BLUE = [0, 0, 255]
    theme = [254, 156, 189]


def main():
    # lang init
    langFile = open(rf'{path}/data/lang.json', encoding='utf-8')
    langJson = langFile.read()
    langFile.close()
    _langData = {}
    _langNow = 'zh'
    try:
        _langData = json.loads(langJson)
    except:
        pass
    if _langData.get(_langNow, False) == False:
        _langNow = list(_langData.keys())[0]

    def langData(key):
        return (_langData[_langNow].get(key, key))

    # settings dictionary
    global settingsDict, settingsKeyImage, settingsValueBtn

    class settingValue:
        def __init__(self, default, type, step=1, range=[1, 10]):
            self.value = default
            self.type = type
            self.step = step
            self.range = range
            if type not in [int, float]:
                self.step = False
                self.range = False

    global _eImagePathNow
    _eImagePathNow = rf'{path}/image/eImage.png'

    settingsDict = {
        "capIndex": settingValue(0, int, step=1, range=[0, 100]),
        "themeColor": settingValue(0, color),
        "scaleRatePerTimes": settingValue(1, float, step=0.1, range=[0, 1.5]),
        "eImagePath": settingValue(_eImagePathNow, 'path')
    }
    settingsDict['themeColor'].value = color.theme

    # pygame init
    pygame.init()
    winW, winH = 500, 300
    winOW, winOH = winW, winH
    win = pygame.display.set_mode((winW, winH), pygame.RESIZABLE)
    pygame.display.set_caption('Vidion Test')

    def drawImage(surface, image, position, resize=False, rotation=False, origin='lt'):
        position = list(position)
        size = image.get_size()
        if resize != False:
            resize = [int(n) for n in resize]
            image = pygame.transform.scale(image, resize)
            size = resize
        if rotation != False:
            image = pygame.transform.rotate(image, rotation)  # deg
            r = rad(rotation % 90)
            size = [
                math.sin(r)*size[1] + math.cos(r)*size[0],
                math.sin(r)*size[0] + math.cos(r)*size[1]
            ]
        origin = 'cc' if origin == 'c' else origin
        for i in range(2):
            if origin[i] in ['a', 'lt'[i]]:
                pass
            elif origin[i] in ['e', 'rb'[i]]:
                position[i] -= size[i]
            elif origin[i] in ['c', 'm']:
                position[i] -= size[i]/2
        surface.blit(image, position)

    def textImage(text='', size=winOW*0.06, bold=False, fgc=color.BLACK, bgc=False, fontName='arial', isSysFont=True):
        # lang font
        fontData = langData('_font')
        if fontData != '_font':
            isSysFont = fontData[0].find('sys') > -1
            fontName = fontData[1].replace(r'{path}', path).replace(
                r'{mode}', 'bold' if bold else 'default')
            size = int(size*fontData[2])
        # render image
        text = str(text)
        font = (pygame.font.SysFont if isSysFont else pygame.font.Font)(
            fontName, size, bold=bold)
        if bgc:
            image = font.render(text, False, fgc, bgc)
        else:
            image = font.render(text, False, fgc)
        return (image)

    def rectTextsImage(text, spaceW, spaceH, bold=False, fgc=color.BLACK, bgc=False, fontName='arial', isSysFont=True, debug=False):
        RTImage = pygame.Surface(
            (spaceW, spaceH), pygame.SRCALPHA).convert_alpha()
        if type(text) == str:
            text = text.split('\n')
        textImageList = [*text]
        lineHeight = spaceH/len(textImageList)
        imageSizeMax = 0
        for i in range(len(textImageList)):
            textImageList[i] = image = textImage(
                textImageList[i], size=lineHeight - winOW*0.01, bold=bold, fgc=fgc, bgc=bgc, fontName=fontName, isSysFont=isSysFont)
            imageWidth = image.get_size()[0]
            imageSizeMax = imageWidth if imageWidth > imageSizeMax else imageSizeMax
        if imageSizeMax > spaceW:
            lineHeight = (lineHeight*spaceW/imageSizeMax)
            for i in range(len(textImageList)):
                image = textImageList[i]
                imageSize = image.get_size()
                textImageList[i] = pygame.transform.scale(image, (int(
                    imageSize[0]/imageSizeMax*spaceW), int(imageSize[1]/imageSizeMax*spaceW)))
        for i, image in enumerate(textImageList):
            drawImage(RTImage, image, position=(
                0, lineHeight*(i+0.5)), origin='lc')
            if debug:
                pygame.draw.rect(
                    RTImage, color.RED, pygame.Rect(0, lineHeight*(i), *image.get_size()), 2)
        if debug:
            pygame.draw.rect(
                RTImage, color.BLUE, pygame.Rect(0, 0, *(int(spaceW), int(spaceH))), 2)
        return (RTImage)

    def setAlpha(image, alpha=100):
        # surface = pygame.Surface(image.get_size(), pygame.SRCALPHA).convert_alpha()
        # surface.set_alpha(alpha)
        # surface.blit(image, (0, 0))
        # return(surface)
        image = image.convert_alpha()
        image.set_alpha(alpha)
        return (image)

    def cv2pg(image, rgbChannel=True):
        image = pygame.image.frombuffer(
            image.tobytes(), image.shape[1::-1], 'BGR' if rgbChannel else 'RGB')
        return (image)

    def pg2cv(image, bgrChannel=True):
        image = pygame.surfarray.array3d(image)
        image = image.transpose([1, 0, 2])
        if bgrChannel:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return (image)

    class button:
        def __init__(self, x=0, y=0, w=10, h=10, fillColor=False, strokeColor=color.BLACK, lineWidth=3, mouseOver=False, mouseLeave=False, mouseClick=False, textImage=False):
            self.x = int(x)
            self.y = int(y)
            self.w = int(w)
            self.h = int(h)
            self.fillColor = fillColor
            self.strokeColor = strokeColor
            self.lineWidth = int(lineWidth)
            self.mouseOver = mouseOver
            self.mouseLeave = mouseLeave
            self._mouseClick = mouseClick
            self._isMouseHovered = False
            self._lastMouseHovered = False
            self.textImage = textImage
            if self.mouseLeave:
                self.mouseLeave(self)

        def setMouseOver(self, function):
            self.mouseOver = function

        def setMouseLeave(self, function):
            self.mouseLeave = function
            if self.mouseLeave:
                self.mouseLeave(self)

        def setMouseClick(self, function):
            self._mouseClick = function

        def draw(self, surface):
            btnRect = [self.x, self.y, self.w, self.h]
            if self.fillColor:
                pygame.draw.rect(
                    surface,
                    self.fillColor,
                    pygame.Rect(*btnRect),
                    width=0
                )
            if self.strokeColor:
                pygame.draw.rect(
                    surface,
                    self.strokeColor,
                    pygame.Rect(*btnRect),
                    width=self.lineWidth
                )
            if self.textImage:
                drawImage(surface, self.textImage, position=[
                          btnRect[0] + btnRect[2]/2, btnRect[1] + btnRect[3]/2], resize=False, rotation=False, origin='c')

        def mouseMove(self, x, y):
            self._isMouseHovered = x >= self.x and x <= self.x + \
                self.w and y >= self.y and y <= self.y+self.h
            if self._isMouseHovered != self._lastMouseHovered:
                self._lastMouseHovered = self._isMouseHovered
                (self.mouseOver if self._isMouseHovered else self.mouseLeave)(self)

        def mouseClick(self):
            if self._mouseClick and self._isMouseHovered:
                self._mouseClick(self)

    # hand detection init
    camW, camH = 640, 480
    capIndexNow = 0
    cap = cv2.VideoCapture(capIndexNow)
    cap.set(3, camW)
    cap.set(4, camH)

    mphands = mp.solutions.hands
    hands = mphands.Hands(min_detection_confidence=0.5,
                          min_tracking_confidence=0.5)
    mpDraw = mp.solutions.drawing_utils

    handLms_style = mpDraw.DrawingSpec(color=(73, 93, 70), thickness=6)  # 特徵點
    handCon_style = mpDraw.DrawingSpec(
        color=(255, 250, 240), thickness=3)  # 特徵點連線

    handDeg = 0

    # fps counter init
    current_time = 0
    previous_time = 0

    # scenes variables
    global scenesNow, scenesNext, transitionMax, transitionTime, transitionMode
    scenesNow = 0  # 0: home, 1: test, 2: settings, 3: about, 4: score
    scenesNext = 0
    transitionMax = 0.5
    transitionTime = transitionMax
    transitionMode = -1

    global btnMouseOver, btnMouseLeave

    def btnMouseOver(btn):
        btn.strokeColor[3] = 255
        btn.textImage = setAlpha(btn.textImage, 255)

    def btnMouseLeave(btn):
        btn.strokeColor[3] = 100
        btn.textImage = setAlpha(btn.textImage, 100)

    def changeScenes(scenes):
        global transitionTime, scenesNext, transitionMode
        scenesNext = scenes
        transitionMode = 1

    # home variables
    global homeTitle, homeTitlePos

    # test variables
    global testMode
    global testBoxRect
    global testBar, testBarRect
    global testImagePos
    global testCamRect, testCamBorder
    global testImageScale
    global userScore
    testImage = pygame.image.load(rf'{path}/image/eImage.png')
    directions = [45*d for d in range(8)]
    testMode = 0  # 0: prepare, 1: show, 2: answer
    testAnswer = 0
    userAnswer = 0
    userAnswer_last = 0
    userAnswerIsCorrect = False
    userDwellTime = 0
    userDwellGate = 0.5
    testAniTime = 0
    testAniLen = 1
    userFlip = True
    testImageScale = 1

    def scaleTestImage(correct=True):
        global testImageScale
        if correct:
            testImageScale *= settingsDict['scaleRatePerTimes'].value
        else:
            testImageScale = max(
                testImageScale / settingsDict['scaleRatePerTimes'].value, testImageScale)

    userScore = {
        'testNum': 0,
        'level': 0,
        'score': 0,
        'time': 0
    }
    userNotCorrectNum = 0
    userNotCorrectMax = 3

    # settings variables
    global colorMapVisible, colorMapImage, colorMapSize, colorMapArray
    colorMapVisible = False
    colorMapImage = pygame.image.load(rf'{path}/image/colorMap.png')
    colorMapSize = colorMapImage.get_size()
    colorMapArray = pg2cv(colorMapImage, False)

    def renderScoreScenes():
        global win_score
        win_score = pygame.Surface(
            (winW, winH), pygame.SRCALPHA).convert_alpha()
        win_score.fill((*color.WHITE, 0))

        userScoreTextList = [[key, '%.2f' % (userScore[key]) if type(
            userScore[key]) == float else userScore[key]] for key in userScore]
        userScoreTextList = [
            f'{kvPair[0]}: {kvPair[1]}' for kvPair in userScoreTextList]
        RTImage = rectTextsImage(
            userScoreTextList, winW - settingsBar.w - winOW*0.02*2, (winH-winOW*(0.02*2)))
        drawImage(win_score, RTImage, position=(
            settingsBar.w + winOW*0.02, winOW*0.02), origin='lt')

    def surfaceResize():
        global btnMouseOver, btnMouseLeave
        global win_alpha
        win_alpha = pygame.Surface(
            (winW, winH), pygame.SRCALPHA).convert_alpha()
        # home
        global homeTitle, homeTitlePos
        homeTitleRect = [0, 0, winW, winOW*0.02 + (winH - winOW*0.02*2)*0.5]
        homeTitlePos = [homeTitleRect[0] + homeTitleRect[2] /
                        2, homeTitleRect[1] + homeTitleRect[3]/2]
        homeTitle = textImage('Vidion Test', size=winOW*0.1, bold=True)
        global startBtn, settingsBtn, aboutBtn
        homeBtnGap = 0.02
        homeBtnRect = [winOW*0.02, winOW*0.02 + (winH - winOW*0.02*2)*0.5, (winW - winOW*(
            homeBtnGap*2 + 0.02*2))/3, (winH - winOW*0.02*2)*0.5]
        settingsBtn = button(
            homeBtnRect[0], *homeBtnRect[1:],
            fillColor=False, strokeColor=[*color.theme, 255], lineWidth=winOW*0.008,
            textImage=textImage(langData('settings'), size=winOW*0.06,
                                fgc=color.theme, bgc=False),
            mouseOver=btnMouseOver, mouseLeave=btnMouseLeave
        )
        startBtn = button(
            homeBtnRect[0] + (homeBtnRect[2] + winOW *
                              homeBtnGap), *homeBtnRect[1:],
            fillColor=False, strokeColor=[*color.theme, 255], lineWidth=winOW*0.008,
            textImage=textImage(langData('start'), size=winOW*0.06,
                                fgc=color.theme, bgc=False),
            mouseOver=btnMouseOver, mouseLeave=btnMouseLeave
        )
        aboutBtn = button(
            homeBtnRect[0] + (homeBtnRect[2] + winOW *
                              homeBtnGap)*2, *homeBtnRect[1:],
            fillColor=False, strokeColor=[*color.theme, 255], lineWidth=winOW*0.008,
            textImage=textImage(langData('about'), size=winOW*0.06,
                                fgc=color.theme, bgc=False),
            mouseOver=btnMouseOver, mouseLeave=btnMouseLeave
        )
        for i, btn in enumerate([startBtn, settingsBtn, aboutBtn]):
            @btn.setMouseClick
            def bmc(*args, i=i):
                global scenesNow
                changeScenes(i+1)
                if i == 0:
                    global testMode, testImageScale, userScore, userNotCorrectNum
                    testMode = 0
                    testImageScale = 1
                    for key in userScore:
                        userScore[key] = 0
                    userScore['level'] = 1
                    userNotCorrectNum = 0
        # test
        global testBoxRect
        testBoxRect = [0, 0, winW, (winH - (winOW*0.02)*2)*0.7 + winOW*0.02]
        global testImagePos
        testImagePos = [testBoxRect[0] + testBoxRect[2] /
                        2, testBoxRect[1] + testBoxRect[3]/2]
        global testBar, testBarRect
        testBarRect = [0, winOW*0.02 + (winH - (winOW*0.02)*2)
                       * 0.7, winW, (winH - (winOW*0.02)*2)*0.3 + winOW*0.02]
        testBar = button(
            *testBarRect,
            fillColor=[*color.theme, 50], strokeColor=False, lineWidth=0
        )
        global testCamRect, testCamBorder
        testCamRect = [False, testBarRect[1] + winOW *
                       0.02, False, testBarRect[3] - winOW*0.02*2]
        testCamRect[2] = testCamRect[3]/camH*camW
        testCamRect[0] = testBarRect[0] + \
            testBarRect[2] - winOW*0.02 - testCamRect[2]
        testCamBorder = button(
            *testCamRect,
            fillColor=False, strokeColor=[*color.theme, 255], lineWidth=winOW*0.008,
            textImage=textImage(langData(''), size=winOW*0.06,
                                fgc=color.theme, bgc=False),
            mouseOver=btnMouseOver, mouseLeave=btnMouseLeave
        )
        global backBtn
        backBtn = button(
            testBarRect[0] + winOW*0.02, testBarRect[1] + winOW *
            0.02, winOW*0.1, testBarRect[3] - winOW*0.02*2,
            fillColor=False, strokeColor=[*color.theme, 255], lineWidth=winOW*0.008,
            textImage=pygame.transform.rotate(
                textImage(langData('exit'), size=winOW*0.06,
                          fgc=color.theme, bgc=False),
                90
            ),
            mouseOver=btnMouseOver, mouseLeave=btnMouseLeave
        )
        @backBtn.setMouseClick
        def bmc(*args): global scenesNow; changeScenes(0)
        # settings
        global settingsBar
        settingsBar = button(
            0, 0, winOW*(0.1+0.02*2), winH,
            fillColor=[*color.theme, 50], strokeColor=False, lineWidth=0
        )
        global settingsDict, settingsKeyImage, settingsValueBtn
        settingsKeyImage = {**settingsDict}
        settingsValueBtn = {**settingsDict}
        for i, key in enumerate(settingsDict):
            settingsKeyImage[key] = textImage(
                langData(key), size=winOW*0.06, fgc=color.BLACK, bgc=False)
            settingsValueBtn[key] = SVBtn = button(
                winOW*(0.1 + 0.02*4) + settingsKeyImage[key].get_size()[
                    0], winOW*(i*0.07 + 0.02), winOW*0.1, winOW*0.06,
                fillColor=[*color.BLACK, 50], strokeColor=[*color.BLACK, 100],
                textImage=textImage('', size=winOW*0.06, fgc=False, bgc=False)
            )
            if settingsDict[key].type == color:
                @SVBtn.setMouseOver
                def bmo(btn):
                    btn.fillColor[3] = 255
                    btn.strokeColor[3] = 255
                    win_alpha.blit

                @SVBtn.setMouseLeave
                def bml(btn):
                    btn.fillColor[3] = 50
                    btn.strokeColor[3] = 100

                @SVBtn.setMouseClick
                def bmc(*args): global colorMapVisible; colorMapVisible = True
            else:
                @SVBtn.setMouseOver
                def bmo(btn):
                    btn.fillColor[3] = 100
                    btn.strokeColor[3] = 255
                    btn.textImage = setAlpha(btn.textImage, 255)
                    win_alpha.blit

                @SVBtn.setMouseLeave
                def bml(btn):
                    btn.fillColor[3] = 50
                    btn.strokeColor[3] = 100
                    btn.textImage = setAlpha(btn.textImage, 100)
                if settingsDict[key].type in [int, float]:
                    @SVBtn.setMouseClick
                    def bmc(self, key=key, type=settingsDict[key].type, valueRange=settingsDict[key].range, valueStep=settingsDict[key].step, *args):
                        mousePos = pygame.mouse.get_pos()
                        innerPos = rectRelativePos(
                            [self.x, self.y, self.w, self.h], mousePos)
                        changeRate = (
                            int(valueStep) if type == int else valueStep)*(1 if innerPos[1] < 0.5 else -1)
                        nextValue = settingsDict[key].value + changeRate
                        maxValue = max(*valueRange)
                        minValue = min(*valueRange)
                        if nextValue > maxValue:
                            nextValue = maxValue
                        elif nextValue < minValue:
                            nextValue = minValue
                        settingsDict[key].value = nextValue
                        if type == float:
                            splitedNum = str(valueStep).split('.')
                            if len(splitedNum) == 2:
                                floatDepth = len(splitedNum[1])
                                if floatDepth > 0:

                                    settingsDict[key].value = float(
                                        round(settingsDict[key].value, floatDepth))
                elif settingsDict[key].type == 'path':
                    @SVBtn.setMouseClick
                    def bmc(self, key=key, *args):
                        global settingsDict
                        filePath = inputFile()
                        settingsDict[key].value = filePath

        # about
        global win_about
        win_about = pygame.Surface(
            (winW, winH), pygame.SRCALPHA).convert_alpha()
        win_about.fill((*color.WHITE, 0))
        RTImage = rectTextsImage(
            DES.split('\n'), winW - settingsBar.w - winOW*0.02*2, (winH-winOW*(0.02*2)))
        drawImage(win_about, RTImage, position=(
            settingsBar.w + winOW*0.02, winOW*0.02), origin='lt')

        # about
        renderScoreScenes()

    surfaceResize()

    # window loop
    run = True
    while run:
        # calculate fps
        current_time = time.time()
        fps = 1/(current_time-previous_time)
        previous_time = current_time

        # cap read
        if capIndexNow != settingsDict['capIndex'].value:
            capIndexNow = settingsDict['capIndex'].value
            cap = cv2.VideoCapture(capIndexNow)
            cap.set(3, camW)
            cap.set(4, camH)
        ret, img = cap.read()
        if not ret:
            img = np.zeros((camH, camW, 3), np.uint8)
        if userFlip:
            img = cv2.flip(img, 1)

        mousePos = pygame.mouse.get_pos()
        # scenes
        if scenesNow == 0:
            # pygame window update
            win.fill(color.WHITE)

            drawImage(win, homeTitle, position=homeTitlePos, origin='c')
            win_alpha.fill((*color.WHITE, 0))
            for btn in [startBtn, settingsBtn, aboutBtn]:
                btn.mouseMove(*mousePos)
                btn.draw(win_alpha)
            win.blit(win_alpha, (0, 0))

            # event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in [startBtn, settingsBtn, aboutBtn]:
                        btn.mouseClick()
        elif scenesNow == 1:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = hands.process(img_rgb)

            img_height = img.shape[0]
            img_width = img.shape[1]

            usingPoints = {}
            if result.multi_hand_landmarks:
                for handLms in result.multi_hand_landmarks:
                    mpDraw.draw_landmarks(
                        img, handLms, mphands.HAND_CONNECTIONS, handLms_style, handCon_style)
                    usingPoints = [[int(lm.x * img_width), int(lm.y * img_height)]
                                   for i, lm in enumerate(handLms.landmark)]
                    # print(handLms.landmark[0].z)

                # 畫出拇指、食指，並連線
                cv2.circle(img, usingPoints[5], 9,
                           color.theme[::-1], cv2.FILLED)
                cv2.circle(img, usingPoints[8], 9,
                           color.theme[::-1], cv2.FILLED)
                cv2.line(img, usingPoints[5],
                         usingPoints[8], color.theme[::-1], 3)
                handDeg = vectorDeg(usingPoints[8], usingPoints[5])
                handVal = vectorVal(usingPoints[8], usingPoints[5])
                handPointing = (vectorVal(usingPoints[0], usingPoints[8]) == max(
                    [vectorVal(usingPoints[0], p) for p in usingPoints]))
                # print(handDeg)

                distances = [*directions]
                for i in range(len(distances)):
                    distances[i] = abs(directions[i] - handDeg)
                    distances[i] = min(distances[i], 360 - distances[i])
                userAnswer = directions[distances.index(min(*distances))]
                if testMode == 1 and userAnswer == userAnswer_last and handPointing:
                    userDwellTime += 1/fps
                else:
                    userDwellTime = 0
                    userAnswer_last = userAnswer
            else:
                userDwellTime = 0

            userScore['time'] += 1/fps
            if testMode == 0:
                testAnswer = random.choice(directions)
                userScore['testNum'] += 1
                testMode = 1
            elif testMode == 1:
                if userDwellTime >= userDwellGate:
                    userDwellTime = 0
                    testAniTime = 0
                    userAnswerIsCorrect = testAnswer == userAnswer
                    if not userAnswerIsCorrect:
                        userNotCorrectNum += 1
                    testMode = 2
            elif testMode == 2:
                testAniTime += 1/fps
                if testAniTime >= testAniLen:
                    if userNotCorrectNum >= userNotCorrectMax:
                        renderScoreScenes()
                        changeScenes(4)
                        userNotCorrectNum = 0
                    scaleTestImage(userAnswerIsCorrect)
                    if userAnswerIsCorrect:
                        userScore['level'] /= settingsDict['scaleRatePerTimes'].value
                    else:
                        userScore['level'] = min(
                            userScore['level'] * settingsDict['scaleRatePerTimes'].value, userScore['level'])
                    userScore['score'] = userScore['testNum'] * \
                        userScore['level']
                    testMode = 0

            # test box
            testImageWidth, testImageHeight = 200, 200
            win.fill(color.WHITE)
            if _eImagePathNow != settingsDict['eImagePath'].value:
                _eImagePathNow = settingsDict['eImagePath'].value
                testImage = pygame.image.load(_eImagePathNow)
            drawImage(win, testImage,
                      position=testImagePos,
                      origin='c',
                      resize=(testImageHeight*testImageScale,
                              testImageWidth*testImageScale),
                      # rotation=handDeg
                      rotation=testAnswer
                      )
            win_alpha.fill((*color.WHITE, 0))
            if testMode == 1:
                pygame.draw.rect(
                    win_alpha,
                    (*color.BLUE, 50),
                    pygame.Rect(testBoxRect[0], testBoxRect[1], int(
                        winW*(userDwellTime/userDwellGate)), testBoxRect[3])
                )
            elif testMode == 2:
                pygame.draw.rect(
                    win_alpha,
                    (*(color.GREEN if userAnswerIsCorrect else color.RED), 50),
                    pygame.Rect(testBoxRect[0], testBoxRect[1], int(
                        winW), testBoxRect[3])
                )
            win.blit(win_alpha, (0, 0))

            # test bar
            win_alpha.fill((*color.WHITE, 0))
            testBar.draw(win_alpha)
            lineHeight = (testBarRect[3]-winOW*(0.02*2))/len(userScore.keys())
            for i, key in enumerate(userScore):
                valueText = '%.2f' % (userScore[key]) if type(
                    userScore[key]) == float else userScore[key]
                USTImage = textImage(
                    f'{langData(key)}: {valueText}', size=lineHeight-winOW*0.01, fgc=color.theme)
                drawImage(win_alpha, USTImage, position=(testBarRect[0] + winOW*(
                    0.02*2+0.1), testBarRect[1] + winOW*(0.02) + lineHeight*(i+0.5)), origin='lc')
                i += 1

            camImage = cv2pg(img)
            drawImage(surface=win_alpha, image=camImage,
                      position=testCamRect[0:2], resize=testCamRect[2:4], origin='lt')
            testCamBorder.mouseMove(*mousePos)
            testCamBorder.draw(win_alpha)
            backBtn.mouseMove(*mousePos)
            backBtn.draw(win_alpha)
            win.blit(win_alpha, (0, 0))

            # event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    backBtn.mouseClick()
        elif scenesNow == 2:
            win.fill(color.WHITE)

            settingsValueBtn['themeColor'].fillColor = [
                *settingsDict['themeColor'].value, 50]
            win_alpha.fill((*color.WHITE, 0))
            for i, key in enumerate(settingsDict):
                value = settingsDict[key]
                drawImage(
                    win_alpha, settingsKeyImage[key], (winOW*(0.1 + 0.02*3), winOW*(i*0.07 + 0.06/2 + 0.02)), origin='lc')
                SVBtn = settingsValueBtn[key]
                if value.type != color:
                    valueText = value.value
                    if value.type == 'path':
                        valueText = valueText.replace('\\', '').split('/')[-1]
                    valueImage = textImage(
                        str(valueText), size=winOW*0.06, fgc=color.BLACK, bgc=False)
                    SVBtn.textImage = valueImage
                    SVBtn.w = winOW*0.02*2 + valueImage.get_size()[0]
                SVBtn.mouseMove(*mousePos)
                SVBtn.draw(win_alpha)
            win.blit(win_alpha, (0, 0))

            camImage = cv2pg(img)
            drawImage(surface=win, image=camImage,
                      position=testCamRect[0:2], resize=testCamRect[2:4], origin='lt')
            testCamBorder.mouseMove(*mousePos)
            testCamBorder.draw(win)

            win_alpha.fill((*color.WHITE, 0))
            settingsBar.draw(win_alpha)
            backBtn.mouseMove(*mousePos)
            backBtn.draw(win_alpha)
            win.blit(win_alpha, (0, 0))

            if colorMapVisible:
                drawImage(win, colorMapImage, position=(0, 0),
                          resize=(winW, winH), origin='lt')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if colorMapVisible:
                        pointedColor = list(colorMapArray[int(
                            mousePos[1]/winH*colorMapSize[1])][int(mousePos[0]/winW*colorMapSize[0])])
                        settingsDict['themeColor'].value = pointedColor
                        color.theme = pointedColor
                        surfaceResize()
                        colorMapVisible = False
                    else:
                        backBtn.mouseClick()
                        for i, key in enumerate(settingsDict):
                            settingsValueBtn[key].mouseClick()
        elif scenesNow == 3:
            win.fill(color.WHITE)

            global win_about
            win.blit(win_about, (0, 0))

            win_alpha.fill((*color.WHITE, 0))
            settingsBar.draw(win_alpha)
            backBtn.mouseMove(*mousePos)
            backBtn.draw(win_alpha)
            win.blit(win_alpha, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    backBtn.mouseClick()
        elif scenesNow == 4:
            win.fill(color.WHITE)

            testImageBg = setAlpha(testImage, 100)
            drawImage(win, testImageBg, position=(winW*3/4, winH*3/4), resize = [min(winW, winH) - winOW*0.02*2 for _ in range(2)], rotation=time.time()*360/5%360, origin='c')

            win.blit(win_score, (0, 0))

            win_alpha.fill((*color.WHITE, 0))
            settingsBar.draw(win_alpha)
            backBtn.mouseMove(*mousePos)
            backBtn.draw(win_alpha)
            win.blit(win_alpha, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    backBtn.mouseClick()
        else:
            changeScenes(0)

        if fps:
            transitionTime += 1/fps*transitionMode
        if transitionTime > transitionMax:
            transitionTime = transitionMax
            transitionMode = -1
            scenesNow = scenesNext
        elif transitionTime < 0:
            transitionTime = 0
        win_alpha.fill((*color.WHITE, 0))
        win_alpha.fill((*color.BLACK, int(transitionTime/transitionMax*255)))
        win.blit(win_alpha, (0, 0))

        pygame.display.update()

        winSize = win.get_size()
        if winW != winSize[0] or winH != winSize[1]:
            winW, winH = winSize
            if winW < winOW:
                winW = winOW
            if winH < winOH:
                winH = winOH
            win = pygame.display.set_mode((winW, winH), pygame.RESIZABLE)
            surfaceResize()


if __name__ == '__main__':
    main()

# 藍道爾氏Ｃ字視力表（Landolt's C Chart）
    # 5 km
# 史奈侖氏Ｅ字視力表（ Snellen's E Chart）
    # 6 km

'''
* 顯示圖片
    * C字
    * E字
    * 自定義
* 播放音量
    * {number}
'''
