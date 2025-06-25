import copy
import itertools
import random
import warnings

import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._allTeams = []
        self._graph = nx.Graph()
        self._idMapTeams = {}
        self._bestPath = []
        self._bestScore = 0

    def getBestPath(self, start):
        self._bestPath = []
        self._bestScore = 0

        parziale = [start]

        vicini = self._graph.neighbors(start)
        for v in vicini:
            parziale.append(v)
            self._ricorsione(parziale)
            parziale.pop()
        return self._bestPath, self._bestScore



    def _ricorsione(self,parziale):
        #1 verifico che parziale sia una soluzione e verifico se migliore della best
        if self.score(parziale) > self._bestScore:
            self._bestScore = self.score(parziale)
            self._bestPath = copy.deepcopy(parziale)

        #2 verifico se posso aggiungere un nuovo nodo
        #3 aggiungo un nodo e faccio la ricorsione

        for v in self._graph.neighbors(parziale[-1]):
            if v not in parziale and self._graph[parziale[-2]][parziale[-1]]["weight"]>self._graph[parziale[-1]][v]["weight"]:
                parziale.append(v)
                self._ricorsione(parziale)
                parziale.pop()


    def getWeightsOfPath(self, path):
        pathTuple = [(path[0], 0)]
        for i in range(1, len(path)):
            pathTuple.append((path[i], self._graph[path[i-1]][path[i]]["weight"]))
        return pathTuple


    def getBestPathV2(self, start):
        self._bestPath = []
        self._bestScore = 0

        parziale = [start]

        vicini = self._graph.neighbors(start)

        viciniTuple = [(v,self._graph[start][v]["weight"]) for v in vicini]
        viciniTuple.sort(key=lambda x:x[1], reverse = True)


        parziale.append(viciniTuple[0][0])
        self._ricorsioneV2(parziale)
        parziale.pop()


        return self.getWeightsOfPath(self._bestPath), self._bestScore



    def _ricorsioneV2(self,parziale):
        #1 verifico che parziale sia una soluzione e verifico se migliore della best
        if self.score(parziale) > self._bestScore:
            self._bestScore = self.score(parziale)
            self._bestPath = copy.deepcopy(parziale)

        #2 verifico se posso aggiungere un nuovo nodo
        #3 aggiungo un nodo e faccio la ricorsione

        vicini = self._graph.neighbors(parziale[-1])

        viciniTuples = [(v, self._graph[parziale[-1]][v]["weight"]) for v in vicini]
        viciniTuples.sort(key=lambda x: x[1], reverse=True)

        for t in viciniTuples:
            if t[0] not in parziale and self._graph[parziale[-2]][parziale[-1]]["weight"]>t[1]:
                parziale.append(t[0])
                self._ricorsioneV2(parziale)
                parziale.pop()
                return



    def score(self, listOfNodes):
        if len(listOfNodes)<2:
            warnings.warn("Errore in score, attesa lista lunga almeno 2.")

        totPeso = 0
        for i in range(len(listOfNodes)-1):
            totPeso += self._graph[listOfNodes[i]][listOfNodes[i+1]]["weight"]

        return totPeso

    def buildGraph(self, year):
        self._graph.clear()
        if len(self._allTeams) == 0:
            print("Lista squadre vuota")
            return
        self._graph.add_nodes_from(self._allTeams)

        #1 modo
        #for n1 in self._graph.nodes:
            #for n2 in self._graph.nodes:
                #if n1 != n2:
                    #self._graph.add_edge(n1,n2)

        #oppure
        #for u in self._allTeams:
            #for v in self._allTeams:
                #if u != v:
                    #self._graph.add_edge(u,v)

        #2 modo
        myedges = list(itertools.combinations(self._allTeams, 2))
        self._graph.add_edges_from(myedges)

        salariesOfTeams = DAO.getSalaryOfTeams(year, self._idMapTeams)
        for e in self._graph.edges:
            self._graph[e[0]][e[1]]["weight"] = salariesOfTeams[e[0]] + salariesOfTeams[e[1]]


    def printGraphDetails(self):
        print(f"Grafo creato con {len(self._graph.nodes)} nodi e {len(self._graph.edges)} archi")

    def getGraphDetails(self):
        return self._graph.number_of_nodes(), self._graph.number_of_edges()



    def getYears(self):
        return DAO.getAllYears()

    def getTeamsOfYear(self, year):
        self._allTeams = DAO.getTeamsOfYear(year)
        self._idMapTeams = {}
        for t in self._allTeams:
            self._idMapTeams[t.ID] = t
        return self._allTeams

    def getNeighborsSorted(self,source):
        #vicini = self._graph.neighbors(source)
        vicini = nx.neighbors(self._graph, source)
        viciniTuple = []
        for v in vicini:
            viciniTuple.append((v,self._graph[source][v]["weight"]))

        viciniTuple.sort(key=lambda x:x[1], reverse=True)
        return viciniTuple

    def getRandomNode(self):
        #mi restituisce un nodo random
        index = random.randint(0, self._graph.number_of_nodes()-1)
        return self._graph.nodes[index]

