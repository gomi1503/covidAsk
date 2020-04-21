from covidask import covidAsk
import argparse
import itertools
import json

import parmap
import multiprocessing

hyperparam_set_id=2
output_path = "evaluation_results_" + str(hyperparam_set_id) + ".tsv"
hyperparam_set_path = "eval_data/hyperparam_" + str(hyperparam_set_id) + ".json"

def do(args, l, errors):
    try: 
        covidask = covidAsk(base_ip = args.base_ip, index_port = args.index_port, args = args)
        res = covidask.eval_request(args)
        l.append((args, res))
        write_result(l)
    except:
        print(args)
        errors.append(args)
    
    return errors

def generate_combinations(hyperparams):
    keys = hyperparams.keys()
    values = (hyperparams[key] for key in keys)
    hyperparam_sets = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

    split_size = int(len(hyperparam_sets) / 3)

    print("SPLIT SIZE:", split_size)

    with open("eval_data/hyperparam_all.json", 'w') as wf:
        json.dump(hyperparam_sets, wf)

    # with open("data/hyperparam_1.json", 'w') as wf:
    #     json.dump(hyperparam_sets[:split_size], wf)
    #
    # with open("data/hyperparam_2.json", 'w') as wf:
    #     json.dump(hyperparam_sets[split_size:split_size*2], wf)
    #
    # with open("data/hyperparam_3.json", 'w') as wf:
    #     json.dump(hyperparam_sets[split_size*2:], wf)

def write_result(evaluation_results):
    with open(output_path, 'w') as wf:
        wf.write("\tModel\tMax answer length\tStart top K\tMid top K\tTop K\tDoc top K\tNprobe\tSparse weight\tSearch strategy\tEM_TOP1\tF1_TOP1\tEM_TOPK\tF1_TOPK\tElapsed time\n")
        for idx in range(len(evaluation_results)):
            _args, res = evaluation_results[idx]
            wf.write(str(idx))
            wf.write('\t')
            wf.write(str(_args.eval_model))
            wf.write('\t')
            wf.write(str(_args.max_answer_length))
            wf.write('\t')
            wf.write(str(_args.start_top_k))
            wf.write('\t')
            wf.write(str(_args.mid_top_k))
            wf.write('\t')
            wf.write(str(_args.top_k))
            wf.write('\t')
            wf.write(str(_args.doc_top_k))
            wf.write('\t')
            wf.write(str(_args.nprobe))
            wf.write('\t')
            wf.write(str(_args.sparse_weight))
            wf.write('\t')
            wf.write(str(_args.search_strategy))
            wf.write('\t')
            wf.write(str(res['exact_match_top1']))
            wf.write('\t')
            wf.write(str(res['f1_score_top1']))
            wf.write('\t')
            wf.write(str(res['exact_match_topk']))
            wf.write('\t')
            wf.write(str(res['f1_score_topk']))
            wf.write('\t')
            wf.write(str(res['time']))
            wf.write('\n')


def main():
    test_path = "eval_data/eval_combined.json"


    # Hyperparameters
    base_ip = "http://localhost"
    ports = {
        'denspi': '9030',
        'denspi_nq': '9031'
    }

    # hyperparams = {
    #     'eval_model': ['denspi', 'denspi_nq'],
    #     'max_answer_length': [20],
    #     'start_top_k': [1000],
    #     'mid_top_k': [100],
    #     'top_k': [30],
    #     'doc_top_k': [5],
    #     'nprobe': [256],
    #     'sparse_weight': [0.05],
    #     'search_strategy': ['hybrid', 'dense_first', 'sparse_first']
    # }
    #
    # generate_combinations(hyperparams)

    with open(hyperparam_set_path, 'r') as rf:
        hyperparam_sets = json.load(rf)

    print("HYPERPARAMETER SET SIZE:", len(hyperparam_sets))

    # evaluation_results = []

    # num_cores = multiprocessing.cpu_count()
    # num_cores = 1
    # manager = multiprocessing.Manager()
    # evaluation_results = manager.list()

    input_list = []
    evaluation_results = []
    error_params = [] 

    for idx, hyperparam in enumerate(hyperparam_sets):
        if idx < 15:
            continue
        if hyperparam['eval_model'] != 'denspi':
            continue

        hyperparam['base_ip'] = base_ip
        hyperparam['index_port'] = ports[hyperparam['eval_model']]

        args = argparse.Namespace(**hyperparam)
        args.draft=False
        args.test_path=test_path
        args.eval_batch_size=10
        args.candidate_path=None
        args.regex=False
        input_list.append(args)
        
        print(args)
        error_params = do(args, evaluation_results, error_params) 
        with open('error_params.json', 'w') as f:
            json.dump(error_params, f)
    # parmap.map(do, input_list, evaluation_results, pm_pbar=True, pm_processes=num_cores)


if __name__ == '__main__':
    main()
