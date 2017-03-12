"""
Takes in two csv files:
1) ground truth file for the relevant document id
2) ranked document id

Outputs precision, recall and F-measure
"""

import os

def get(f1, f2 = 'Time_REL.csv'):
    def get_average(lst):
        return sum(lst)/float(len(lst))

    groundTruth = open(f2, 'r').readlines() # each line represents a list of relevant docs
    retrieved = open(f1, 'r').readlines()   # each line represents a list of retrieved docs

    for i in range(1): # number of queries
        precision = []
        recall = []
        f_measure = []

        temp_precision = []
        temp_recall = []
        temp_f_measure = []

        relevant_docs = groundTruth[i].strip().split(',')[1:]
        returned_docs = retrieved[i].strip().split(',')[1:]
        num_tot_relevant = len(relevant_docs)

        for j in range(len(returned_docs)):
            to_compare = returned_docs[:j+1]
            p_j = len(set(to_compare).intersection(relevant_docs))/float((j+1))
            r_j = len(set(to_compare).intersection(relevant_docs))/float(num_tot_relevant)
            if p_j == 0 and r_j == 0:
                f_j = 0
            else:
                f_j = (2 * p_j * r_j) / (p_j + r_j)
            temp_precision.append(p_j)
            temp_recall.append(r_j)
            temp_f_measure.append(f_j)

        # store all precision, recall and f measure for one query
        # list of lists [0] <- precision for query 1
        precision.append(temp_precision)
        recall.append(temp_recall)
        f_measure.append(temp_f_measure)

    precision_k = []
    recall_k = []
    f_measure_k = []

    k = len(precision[0])

    for j in range(k):  # for each position

        total_precision = 0
        total_recall = 0
        total_f_measure = 0

        for i in range(len(precision)): # for each query
            total_precision += precision[i][j]
            total_recall += recall[i][j]
            total_f_measure += f_measure[i][j]

        precision_k.append(total_precision / len(precision))
        recall_k.append(total_recall / len(recall))
        f_measure_k.append(total_f_measure / len(f_measure))

    file_dir = 'Evals_{}.csv'.format(f1.replace('.csv', ''))

    output = open(file_dir, 'w')

    output.write(','.join(str(j) for j in precision_k))
    output.write('\n')
    output.write(','.join(str(j) for j in recall_k))
    output.write('\n')
    output.write(','.join(str(j) for j in f_measure_k))
    output.write('\n')
    output.close()


if __name__ == '__main__':
    files = os.listdir(os.getcwd())
    for file in files:
        if not file.startswith("__") and not file.endswith(".py") \
                and file != 'Time_REL.csv' and not file.startswith("Evals_"):
            get(file)

