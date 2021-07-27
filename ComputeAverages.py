import math


def read_file(judgements, r):
    f_debug = open('debug_file.txt', 'a+')

    # path_results = 'hw4-bm25-baseline-j623lee.txt'
    # results_files = ['student1', 'student2', 'student3', 'student4', 'student5', 'student6', 'student7', 'student8', 'student9', 'student10', 'student11', 'student12', 'student13', 'student14', 'msmuckerAND']
    results_files = ['hw4-bm25-baseline-j623lee.txt', 'hw4-bm25-stem-j623lee.txt']

    # === Calculate Averages ===
    with open('hw4-metrics-j623lee.txt', 'w+') as f:
        headers = ['Run Name', 'Mean Average Precision', 'Mean P@10', 'Mean NDCG@10', 'Mean NDCG@1000', 'Mean TBG']
        f.write(','.join(headers))

    for file in results_files: # Iterate through run files
        print(file)
        f = open(file, 'rb+')
        lines = f.read().splitlines()

        f_debug.write(file+'\n')
        results = {}
        good_format = True
        for l in lines:
            topic = str(l, 'utf-8').split(' ')
            if not proper_format(topic):
                good_format = False
                break
            topic_id = topic[0]
            docno = topic[2]
            score = float(topic[4])

            if topic_id not in results:
                results[topic_id] = [[docno, score]]
            else:
                results[topic_id].append([docno, score])

        # Store docno by descending score, not ranking
        for topic in results:
            results[topic].sort(key=lambda x:x[1], reverse=True)

        f_5a = open('hw4-metrics-j623lee.txt', 'a+')
        if good_format:
            map = []
            mean_p_10 = []
            mean_ndcg_10 = []
            mean_ndcg_1000 = []
            mean_tbg = []
            topics = []
            for topic in results: # Iterate through topic queries
                f_debug.write(topic+'\n')
                topics.append(topic)
                ap = 0
                p = []
                p_10 = 0
                dcg_10 = 0
                dcg_1000 = 0
                idcg_10 = 0
                idcg_1000 = 0
                t_d = []
                pr = []
                tbg = []

                for i in range(len(results[topic])): # Iterate through query results
                    docno = results[topic][i][0]
                    f_debug.write(docno+'\n')
                    if topic+docno in judgements:
                        r_i = int(judgements[topic+docno])
                    else:
                        r_i = 0
                    p.append(r_i) #Relevant
                    p_i = sum(p)/len(p)

                    ap += r_i * p_i
                    if i < 10:
                        p_10 += r_i
                        dcg_10 += r_i/math.log2(i+2)
                    if i < 1000:
                        dcg_1000 += r_i/math.log2(i+2)

                    if r_i == 1:
                        pr.append(0.64)
                    else:
                        pr.append(0.39)

                    mm = docno[2:4]
                    dd = docno[4:6]
                    yy = docno[6:8]
                    path = '/'.join(['latimes-index-baseline', yy, mm, dd, docno+'.txt'])
                    f = open(path, 'rb+')
                    metadata = f.readlines()
                    f.close()
                    l = int(str(metadata[-1], 'utf-8').split(' ')[1]) # Check with metadata[3] for titles on two lines
                    t_d.append(0.018*l+7.8)

                    t_k = 0
                    for j in range(i): # Iterate through all previous query results
                        t_k += 4.4 + t_d[j]*pr[j]

                    d_t = math.exp(-t_k * math.log(2) / 224)
                    tbg.append(r_i * 0.64 * 0.77 * d_t)

                map.append(ap/r[topic])
                mean_p_10.append(p_10/10)
                mean_tbg.append(sum(tbg))

                # Calculate idcg
                for i in range(min(10, r[topic])):
                    idcg_10 += 1/math.log2(i+2)
                for i in range(min(1000, r[topic])):
                    idcg_1000 += 1/math.log2(i+2)

                if dcg_10==0 and idcg_10==0:
                    ndcg_10 = 0
                else:
                    ndcg_10 = dcg_10/idcg_10

                if dcg_1000==0 and idcg_1000==0:
                    ndcg_1000 = 0
                else:
                    ndcg_1000 = dcg_1000/idcg_1000
                mean_ndcg_10.append(ndcg_10)
                mean_ndcg_1000.append(ndcg_1000)

            # Write averages to output file in readable format
            output_file = file+'_output.csv'
            with open(output_file, 'a+') as f:
                # Add AP
                for i in range(len(topics)):
                    f.write((',').join(['ap', topics[i], "{:.3f}\n".format(map[i])]))
                # Add ndcg_cut_10
                for i in range(len(topics)):
                    f.write((',').join(['ndcg_cut_10', topics[i], "{:.3f}\n".format(mean_ndcg_10[i])]))
                # Add ndcg_cut_1000
                for i in range(len(topics)):
                    f.write((',').join(['ndcg_cut_1000', topics[i], "{:.3f}\n".format(mean_ndcg_1000[i])]))
                # Add P_10
                for i in range(len(topics)):
                    f.write((',').join(['P_10', topics[i], "{:.3f}\n".format(mean_p_10[i])]))
                # Add tbg
                for i in range(len(topics)):
                    f.write((',').join(['tbg', topics[i], "{:.3f}\n".format(mean_tbg[i])]))

        # Calculate Averages
            map = sum(map)/len(map)
            mean_p_10 = sum(mean_p_10)/len(mean_p_10)
            mean_ndcg_10 = sum(mean_ndcg_10)/len(mean_ndcg_10)
            mean_ndcg_1000 = sum(mean_ndcg_1000)/len(mean_ndcg_1000)
            mean_tbg = sum(mean_tbg)/len(mean_tbg)
            averages = ['\n'+file, "{:.3f}".format(map), "{:.3f}".format(mean_p_10), "{:.3f}".format(mean_ndcg_10), "{:.3f}".format(mean_ndcg_1000), "{:.3f}".format(mean_tbg)]
            f_5a.write(','.join(averages))
        else:
            map = 'bad format'
            mean_p_10 = 'bad format'
            mean_ndcg_10 = 'bad format'
            mean_ndcg_1000 = 'bad format'
            mean_tbg = 'bad format'
            averages = ['\n'+file, map, mean_p_10, mean_ndcg_10, mean_ndcg_1000, mean_tbg]
            f_5a.write(','.join(averages))

        # Add averages for results file to csv
        print('Done')



def proper_format(result):
    is_proper_format = True
    if len(result) != 6:
        print("ERROR: Results file should have 6 columns")
        is_proper_format = False
    elif len(result[2]) != 13:
        print("ERROR: Docno length incorrect")
        is_proper_format = False
    elif result[2][0:2] != 'LA' or result[2][8] != '-':
        print("ERROR: Docno incorrect format detected")
        is_proper_format = False
    return is_proper_format


def add_line(file, line):
    file.write(','.join(line))


def get_judgements():
    path_qrels = 'hw3-files-2021/upload-to-learn/qrels/LA-only.trec8-401.450.minus416-423-437-444-447.txt'
    f = open(path_qrels, 'rb+')
    lines = f.read().splitlines()

    judgements = {} # Map of topic docno to relevancy judgement
    r = {} # Map of |R| values for each topic
    for l in lines:
        topic = str(l, 'utf-8').split(' ')
        topic_id = topic[0]
        docno = topic[2]
        judgement = topic[3]

        judgements[topic_id+docno] = judgement # Retrieve relevance by going judgements[topic_id+docno]
        if judgement == '1':
            if topic_id not in r:
                r[topic_id] = 1
            else:
                r[topic_id] += 1

    return judgements, r


if __name__ == "__main__":
    judgements, r = get_judgements()
    read_file(judgements, r)
