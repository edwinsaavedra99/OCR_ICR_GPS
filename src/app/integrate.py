from __future__ import division
from __future__ import print_function

import sys
import argparse
from os.path import isfile, join

import cv2
import editdistance
from DataLoader import DataLoader, Batch
from Model import Model, DecoderType
from SamplePreprocessor import preprocess
import os
from WordSegmentation import wordSegmentation, prepareImg


class FilePaths:
    "filenames and paths to data"
    fnCharList = '../model/charList.txt'
    fnAccuracy = '../model/accuracy.txt'
    fnTrain = '../data/'
    fnInfer = '../data/rf-test1.png'
    fnInfer2 = '../data/test.png'
    fnCorpus = '../data/corpus.txt'


def train(model, loader):
    "train NN"
    epoch = 0  # number of training epochs since start
    bestCharErrorRate = float('inf')  # best valdiation character error rate
    noImprovementSince = 0  # number of epochs no improvement of character error rate occured
    earlyStopping = 5  # stop training after this number of epochs without improvement
    while True:
        epoch += 1
        print('Epoch:', epoch)

        # train
        print('Train NN')
        loader.trainSet()
        while loader.hasNext():
            iterInfo = loader.getIteratorInfo()
            batch = loader.getNext()
            loss = model.trainBatch(batch)
            print('Batch:', iterInfo[0], '/', iterInfo[1], 'Loss:', loss)

        # validate
        charErrorRate = validate(model, loader)

        # if best validation accuracy so far, save model parameters
        if charErrorRate < bestCharErrorRate:
            print('Character error rate improved, save model')
            bestCharErrorRate = charErrorRate
            noImprovementSince = 0
            model.save()
            open(FilePaths.fnAccuracy, 'w').write(
                'Validation character error rate of saved model: %f%%' % (charErrorRate * 100.0))
        else:
            print('Character error rate not improved')
            noImprovementSince += 1

        # stop training if no more improvement in the last x epochs
        if noImprovementSince >= earlyStopping:
            print('No more improvement since %d epochs. Training stopped.' % earlyStopping)
            break


def validate(model, loader):
    "validate NN"
    print('Validate NN')
    loader.validationSet()
    numCharErr = 0
    numCharTotal = 0
    numWordOK = 0
    numWordTotal = 0
    while loader.hasNext():
        iterInfo = loader.getIteratorInfo()
        print('Batch:', iterInfo[0], '/', iterInfo[1])
        batch = loader.getNext()
        (recognized, _) = model.inferBatch(batch)

        print('Ground truth -> Recognized')
        for i in range(len(recognized)):
            numWordOK += 1 if batch.gtTexts[i] == recognized[i] else 0
            numWordTotal += 1
            dist = editdistance.eval(recognized[i], batch.gtTexts[i])
            numCharErr += dist
            numCharTotal += len(batch.gtTexts[i])
            print('[OK]' if dist == 0 else '[ERR:%d]' % dist, '"' + batch.gtTexts[i] + '"', '->',
                  '"' + recognized[i] + '"')

    # print validation result
    charErrorRate = numCharErr / numCharTotal
    wordAccuracy = numWordOK / numWordTotal
    print('Character error rate: %f%%. Word accuracy: %f%%.' % (charErrorRate * 100.0, wordAccuracy * 100.0))
    return charErrorRate


def infer(model, fnImg):
    "recognize text in image provided by file path"
    img = preprocess(cv2.imread(fnImg, cv2.IMREAD_GRAYSCALE), Model.imgSize)
    batch = Batch(None, [img])
    (recognized, probability) = model.inferBatch(batch, True)
    print('Recognized:', '"' + recognized[0] + '"')
    print('Probability:', probability[0])
    return recognized[0],probability[0]


def segmentation():
    """reads images from data_in/ and outputs the word-segmentation to out/"""

    # read input images from 'in' directory
    imgFiles = os.listdir('../data_in/')
    for (i, f) in enumerate(imgFiles):
        print('Segmenting words of sample %s' % f)

        # read image, prepare it by resizing it to fixed height and converting it to grayscale
        img = prepareImg(cv2.imread('../data_in/%s' % f), 50)

        # execute segmentation with given parameters
        # -kernelSize: size of filter kernel (odd integer)
        # -sigma: standard deviation of Gaussian function used for filter kernel
        # -theta: approximated width/height ratio of words, filter function is distorted by this factor
        # - minArea: ignore word candidates smaller than specified area
        res = wordSegmentation(img, kernelSize=25, sigma=11, theta=7, minArea=100)

        # write output to 'out/inputFileName' directory
        if not os.path.exists('../out/%s' % f):
            os.mkdir('../out/%s' % f)

        # iterate over all segmented words
        print('Segmented into %d words' % len(res))
        for (j, w) in enumerate(res):
            (wordBox, wordImg) = w
            (x, y, w, h) = wordBox
            cv2.imwrite('../out/%s/%d.png' % (f, j), wordImg)  # save word
            cv2.rectangle(img, (x, y), (x + w, y + h), 0, 1)  # draw bounding box in summary image

        # output summary image with bounding boxes around words
        cv2.imwrite('../out/%s/summary.png' % f, img)



def icrMain():
    "main function"
    # optional command line args
    rpta = ''
    prob = 0
    number_of_files = 1
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', help='train the NN', action='store_true')
    parser.add_argument('--validate', help='validate the NN', action='store_true')
    parser.add_argument('--beamsearch', help='use beam search instead of best path decoding', action='store_true')
    parser.add_argument('--wordbeamsearch', help='use word beam search instead of best path decoding',
                        action='store_true')
    parser.add_argument('--dump', help='dump output of NN to CSV file(s)', action='store_true')

    args = parser.parse_args()

    decoderType = DecoderType.BestPath
    if args.beamsearch:
        decoderType = DecoderType.BeamSearch
    elif args.wordbeamsearch:
        decoderType = DecoderType.WordBeamSearch

    # train or validate on IAM dataset
    if args.train or args.validate:

        # load training data, create TF model
        loader = DataLoader(FilePaths.fnTrain, Model.batchSize, Model.imgSize, Model.maxTextLen)

        # save characters of model for inference mode
        open(FilePaths.fnCharList, 'w').write(str().join(loader.charList))

        # save words contained in dataset into file
        open(FilePaths.fnCorpus, 'w').write(str(' ').join(loader.trainWords + loader.validationWords))

        # execute training or validation
        if args.train:
            model = Model(loader.charList, decoderType)
            train(model, loader)
        elif args.validate:
            model = Model(loader.charList, decoderType, mustRestore=True)
            validate(model, loader)

    # infer text on test image
    else:
        print("------ start processing ------ ")
        print(open(FilePaths.fnAccuracy).read())
        model = Model(open(FilePaths.fnCharList).read(), decoderType, mustRestore=True, dump=args.dump)
        # crear
        rpta = ''
        prob = 0
        segmentation()
        directory = '../out/0.png'
        number_of_files = sum(1 for item in os.listdir(directory) if isfile(join(directory, item)))-1
        for j in range(number_of_files):
            FilePaths.fnInfer = '../out/0.png/'+str(j)+'.png'
            aux1,aux2 = infer(model, FilePaths.fnInfer)
            rpta+=str(aux1)+' '
            prob+=aux2
        print(rpta)
    return rpta, prob/number_of_files
        #infer(model, FilePaths.fnInfer)
        #infer(model, FilePaths.fnInfer2)


if __name__ == '__main__':
    icrMain()

