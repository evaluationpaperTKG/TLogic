# this file has been modified by authors of evaluation paper for TGL Neurips workshop
# all changes can be seen via git diff, and are marked with a comment containing "eval_paper_authors"

import json
import numpy as np


class Grapher(object):
    def __init__(self, dataset_dir):
        """
        Store information about the graph (train/valid/test set).
        Add corresponding inverse quadruples to the data.

        Parameters:
            dataset_dir (str): path to the graph dataset directory

        Returns:
            None
        """

        self.dataset_dir = dataset_dir
        self.entity2id = json.load(open(dataset_dir + "entity2id.json"))
        self.relation2id_old = json.load(open(dataset_dir + "relation2id.json"))
        self.relation2id = self.relation2id_old.copy()
        counter = len(self.relation2id_old)
        for relation in self.relation2id_old:
            self.relation2id["_" + relation] = counter  # Inverse relation
            counter += 1
        ###  modified "eval_paper_authors" to use unified datasets which do not have the names but directly the ids
        try:
            self.ts2id = json.load(open(dataset_dir + "ts2id.json"))
        except:
            print('no file ts2id.json')
        self.id2entity = dict([(int(v), k) for k, v in self.entity2id.items()]) #eval_paper_authors
        self.id2relation = dict([(int(v), k) for k, v in self.relation2id.items()]) #eval_paper_authors
        # self.id2entity = dict([(v, k) for k, v in self.entity2id.items()])
        # self.id2relation = dict([(v, k) for k, v in self.relation2id.items()])
        # self.id2ts = dict([(v, k) for k, v in self.ts2id.items()])
        ## end modified eval_paper_authors
        
        self.inv_relation_id = dict()
        num_relations = len(self.relation2id_old)
        for i in range(num_relations):
            self.inv_relation_id[i] = i + num_relations
        for i in range(num_relations, num_relations * 2):
            self.inv_relation_id[i] = i % num_relations

        self.train_idx = self.create_store("train.txt")
        self.valid_idx = self.create_store("valid.txt")
        self.test_idx = self.create_store("test.txt")
        self.all_idx = np.vstack((self.train_idx, self.valid_idx, self.test_idx))

        print("Grapher initialized.")

    def create_store(self, file):
        """
        Store the quadruples from the file as indices.
        The quadruples in the file should be in the format "subject\trelation\tobject\ttimestamp\n".

        Parameters:
            file (str): file name

        Returns:
            store_idx (np.ndarray): indices of quadruples
        """

        with open(self.dataset_dir + file, "r", encoding="utf-8") as f:
            quads = f.readlines()
        store = self.split_quads(quads)
        store_idx = self.map_to_idx(store)
        store_idx = self.add_inverses(store_idx)

        return store_idx

    def split_quads(self, quads):
        """
        Split quadruples into a list of strings.

        Parameters:
            quads (list): list of quadruples
                          Each quadruple has the form "subject\trelation\tobject\ttimestamp\n".

        Returns:
            split_q (list): list of quadruples
                            Each quadruple has the form [subject, relation, object, timestamp].
        """

        split_q = []
        for quad in quads:
            split_q.append(quad[:-1].split("\t"))

        return split_q

    def map_to_idx(self, quads):
        """
        Map quadruples to their indices.

        Parameters:
            quads (list): list of quadruples
                          Each quadruple has the form [subject, relation, object, timestamp].

        Returns:
            quads (np.ndarray): indices of quadruples
        """
        ## modified eval_paper_authors for datasets with ids 
        # subs =  [self.entity2id[x[0]] for x in quads]
        # rels = [self.relation2id[x[1]] for x in quads]
        # objs = [self.entity2id[x[2]] for x in quads]

        subs = [int(x[0]) for x in quads] # [self.entity2id[x[0]] for x in quads]
        rels = [int(x[1]) for x in quads] #[self.relation2id[x[1]] for x in quads]
        objs = [int(x[2]) for x in quads] #[self.entity2id[x[2]] for x in quads]
        # end eval_paper_authors

        ts =  set([x[3] for x in quads])
        self.ts2id = {tsvalu:int(int(tsvalu)) for tsvalu in ts} #{value: idx for idx, value in enumerate((ts))} #maps ts2indeces
        self.id2ts = dict([(v, k) for k, v in self.ts2id.items()])

        tss = [self.ts2id[x[3]] for x in quads]
        quads = np.column_stack((subs, rels, objs, tss))

        return quads

    def add_inverses(self, quads_idx):
        """
        Add the inverses of the quadruples as indices.

        Parameters:
            quads_idx (np.ndarray): indices of quadruples

        Returns:
            quads_idx (np.ndarray): indices of quadruples along with the indices of their inverses
        """

        subs = quads_idx[:, 2]
        rels = [self.inv_relation_id[x] for x in quads_idx[:, 1]]
        objs = quads_idx[:, 0]
        tss = quads_idx[:, 3]
        inv_quads_idx = np.column_stack((subs, rels, objs, tss))
        quads_idx = np.vstack((quads_idx, inv_quads_idx))

        return quads_idx
