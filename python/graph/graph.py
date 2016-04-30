"""Graph module is not thread safe due to state.
"""
import numpy as np
import logging

FORMAT = '%(asctime)s::%(levelname)s::%(name)s::%(funcName)s::%(message)s'
logging.basicConfig(
    format=FORMAT,
    level=logging.DEBUG)
logger = logging.getLogger("DAG")

class Graph(object):
    
    def __init__(self, ):
        """Directed Acyclic Graph
        Graph represents a set of Vertex and Edge, or G = (V, E).
        """
        self.vertices = set()
        self.edges = set()

    def find_vertices(self, name=None):
        """Find
        """
        pass
        
    def find_edges(self, name=None):
        """Find
        """
        pass

dag = Graph()

class Edge(object):
    """Edge
    """
    
    def __init__(self, name=None):
        self._graph = dag

        self.in_vertices = []
        self.out_vertex = None
        self.name = name

        # Add to graph
        self._graph.edges.add(self)

    def __call__(self, *vertices):
        return self.add(*vertices)
        
    def add(self, *vertices):
        """Add vertices and return a new vertex
        """
        # Create a new vertex,
        # then add an edge as input and add the vertex as output
        new_vertex = Vertex(name="output-{}".format(self.name))
        new_vertex.in_edge = self
        self.out_vertex = new_vertex

        # Add vertices as input and add edges as output
        for vertex in vertices:
            vertex.out_edges.append(self)
            self.in_vertices.append(vertex)

        return new_vertex

    def forward(self, inputs):
        # Concatenation case
        if len(self.in_vertices) > 1:
            if not hasattr(self, "in_cnt"):
                self.in_cnt = len(self.in_vertices)
                self.inputs = []
            self.in_cnt -= 1

            # Return inputs itself
            if self.in_cnt != 0:
                self.inputs.append(inputs)
                return inputs

            # Compute something for each here, just elemwise-sum now
            del self.in_cnt
            self.inputs.append(inputs)
            output = self.infer(self.inputs)
            logger.debug("edge({}).forward".format(self.name))
            return self.out_vertex.forward(output)

        # Compute Inference
        output = self.infer(inputs)

        logger.debug("edge({}).forward".format(self.name))
        return self.out_vertex.forward(output)

    def infer(self, inputs):
        """Infer given inputs

        Parameters
        -----------------
        inputs: ndarray or list of ndarray

        Returns
        -----------
        ndarray
        
        """
        if inputs == []:
            return reduce(lambda x, y: x + y, inputs)

        return inputs
        
    def backward(self, grad):
        logger.debug("edge({}).backword".format(self.name))

        # Compute Gradients
        grads = self.grads(grad, [v.value for v in self.in_vertices])

        grad_ = self.in_vertices[0].backward(grads[0])
        for grad__, in_vertex in zip(grads[1:], self.in_vertices[1:]):
            grad_ += in_vertex.backward(grad__)

        return grad_

    def grads(self, grad, inputs):
        """Grad given input and grad
        Parameters
        -----------------
        grad: ndarray
        inputs: ndarray or list of ndarray

        Returns
        -----------
        list of ndarray
        """
        return [grad * in_ for in_ in inputs]
        
class Vertex(object):
    """Vertex
    """
    
    def __init__(self, name=None):
        self._graph = dag

        self.in_edge = None
        self.out_edges = []
        self.name = name
        self.value = None
        self.grad = None
        
        # Add to graph
        self._graph.vertices.add(self)

    def forward(self, in_):
        logger.debug("vertex({}).forward".format(self.name))

        out_ = in_
        self.value = out_
        if self.out_edges != []:
            return reduce(lambda x, y: x + y,
                          [e.forward(out_) for e in self.out_edges])

        return in_
        
    def backward(self, grad):
        # Concatenation case
        if len(self.out_edges) > 1:
            self.out_cnt = len(self.out_edges) \
                              if not hasattr(self, "out_cnt") else self.out_cnt
            self.out_cnt -= 1

            # Return grad itself
            if self.out_cnt != 0:
                self.grad = grad
                return grad

            # Call backward
            del self.out_cnt
            self.grad += grad
            grad_ = self.grad

            if self.in_edge is not None:
                logger.debug("vertex({}).backward".format(self.name))
                return self.in_edge.backward(grad_)

            # Input vertex case
            return grad

        self.grad = grad

        if self.in_edge is not None:
            logger.debug("vertex({}).backward".format(self.name))
            return self.in_edge.backward(grad)

        return grad

class SquareLoss(Edge):
    
    def __init__(self,  name=None):
        super.__init__(SquareLoss, name=name)
        
    def infer():
        pass
            

        
def main():

    v0 = Vertex("x")
    v1 = Edge(name="e0")(v0)
    v2 = Edge(name="e1")(v1)
    v3 = Edge(name="e2")(v2, v1)
    v4 = Edge(name="e3")(v3)
    v5 = Edge(name="e4")(v4)

    print "----- Vertices and Edges in Graph -----"
    print len(dag.vertices)
    print len(dag.edges)

    print "----- Forward pass -----"
    inputs = np.random.rand(10, 5)
    print v0.forward(inputs)

    print "----- Backward pass -----"
    grad = np.random.rand(10, 5)
    print v5.backward(grad)

if __name__ == '__main__':
    main()

