"""
Takes in two csv files:
1) ground truth file for the relevant document id
2) ranked document id

Outputs precision, recall and F-measure
"""

def getMetrics(f1, f2 = 'Time_REL.csv'):
    def get_average(lst):
        return sum(lst)/float(len(lst))

    groundTruth = open(f2, 'r').readlines() # each line represents a list of relevant docs
    retrieved = open(f1, 'r').readlines()   # each line represents a list of retrieved docs

    groundTruth.close()
    retrieved.close()

    precision = []
    recall = []
    f_measure = []

    for i in range(len(groundTruth)): # number of queries

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
            f_j = (2 * p_j * r_j) / (p_j + r_j)
            temp_precision.append(p_j)
            temp_recall.append(r_j)
            temp_f_measure(f_j)

        precision.append(get_average(temp_precision))
        recall.append(get_average(temp_recall))
        f_measure.append(get_average(f_measure))

    return precision, recall, f_measure