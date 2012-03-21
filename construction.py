"""

flagmatic 2

Copyright (c) 2012, E. R. Vaughan. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1) Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2) Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import sys

from sage.all import Integer, QQ, matrix, factorial, identity_matrix
from sage.structure.sage_object import SageObject


class Construction(SageObject):

	def __init__(self):
		pass

	@property
	def field(self):
		return RationalField()

	def edge_density(self):
		return 0

	def subgraph_densities(self, n):
		return None

	def target_bound(self):
		return None

	def zero_eigenvectors(self, tg, flags, flag_basis=None):
		return None


class AdHocConstruction(Construction):

	def __init__(self, name):

		self._name = name

		if name == "maxs3":
	
			self._field_str = "NumberField(x^2+x-1/2, 'x', embedding=0.5)"
	
		elif name == "maxs4":

			self._field_str = "NumberField(x^3+x^2+x-1/3, 'x', embedding=0.5)"

		elif name == "maxs5":

			self._field_str = "NumberField(x^4+x^3+x^2+x-1/4, 'x', embedding=0.5)"

		else:
		
			self._field_str = "RationalField()"
		
		x = polygen(QQ)
		self._field = sage_eval(self._field_str, locals={'x': x})


	@property
	def field(self):
		return self._field
	

	def target_bound(self):

		K = self._field
		x = K.gen()

		if self._name == "maxs3":

			return (4 * x - 1, [0, 2, 4, 5])

		elif self._name == "maxs4":
		
			return (1 - 9 * x**2, [0, 5, 8, 16, 24, 27, 29, 31, 37, 38, 41])

		elif self._name == "max42":

			return (Integer(3)/4, [0, 4, 8, 23, 24, 27, 33])


	def zero_eigenvectors(self, tg, flags, flag_basis=None):
	
		K = self._field
		x = K.gen()
		
		rows = []

		# TODO: should check flags are in the right order!
		
		if self._name == "maxs3":

			if tg.is_equal(Flag("1:", 2, True)):
		
				rows = [
					[1 - x,       0,     x],
					[x * (1 - x), 1 - x, x**2]
				]
	
		elif self._name == "maxs4":

			if tg.is_equal(Flag("2:", 2, True)):
		
				rows = [
					[1 - x,       0, 0, 0, 0, 0,   0, 0, x],
					[x * (1 - x), 0, 0, 0, 0, 1-x, 0, 0, x**2]
				]
				
			elif tg.is_equal(Flag("2:12", 2, True)):

				rows = [
					[0, 1 - x, 0, 0, 0, 0, 0, 0, x],
					[0, 0,     0, 0, 1, 0, 0, 0, -1],
					[0, 0,     0, 0, 0, 1, 0, 0, 0],
					[0, 0,     0, 0, 0, 0, 1, 0, -1]
				]

		elif self._name == "max42":

			if tg.is_equal(Flag("3:")):

				rows = [[1, 0, 0, 0, 1, 1, 1, 0]]
			
			elif tg.is_equal(Flag("3:123")):

				rows = [[0, 1, 1, 1, 0, 0, 0, 1]]

		if len(rows) == 0:
			return matrix(K, 0, flag_basis.nrows(), sparse=True)

		if flag_basis is None:
			flag_basis = identity_matrix(QQ, len(flags))

		M = matrix(K, list(rows), sparse=True) * flag_basis.T
		
		if M.rank() == 0:
			return matrix(K, 0, flag_basis.nrows(), sparse=True)
		
		M = M.echelon_form()
		M = M[:M.rank(),:]

		return M


class BlowupConstruction(Construction):

	def __init__(self, g):
	
		if g.oriented:
			raise NotImplementedException("oriented graphs not supported.")
	
		self._graph = g
	
	
	def edge_density(self):
	
		den_pairs = self.subgraph_densities(self._graph.r)

		for pair in den_pairs:
			g, den = pair
			if g.ne == 1:
				return den		
	
		
	def subgraph_densities(self, n):

		cn = self._graph.n
		total = Integer(0)
		sharp_graph_counts = {}
		sharp_graphs = []

# An "inefficient" alternative (sometimes it is faster...UnorderedTuples might have overhead)
# 		for P in Tuples(range(1, cn + 1), n):
# 			factor = 1
		
		for P in UnorderedTuples(range(1, cn + 1), n):
		
			factor = factorial(n)
			
			for i in range(1, cn + 1):
				factor /= factorial(P.count(i))
				
			ig = self._graph.degenerate_induced_subgraph(P)
			ig.make_minimal_isomorph()
			
			ghash = hash(ig)
			if ghash in sharp_graph_counts:
				sharp_graph_counts[ghash] += factor
			else:
				sharp_graphs.append(ig)
				sharp_graph_counts[ghash] = factor

			total += factor
		
		return [(g, sharp_graph_counts[hash(g)] / total) for g in sharp_graphs]


	def zero_eigenvectors(self, tg, flags, flag_basis=None):
	
		rows = set()
		for tv in Tuples(range(1, self._graph.n + 1), tg.n):
			rows.add(tuple(self._graph.degenerate_flag_density(tg, flags, tv)))

		if flag_basis is None:
			flag_basis = identity_matrix(QQ, len(flags))
	
		if len(rows) == 0:
			return matrix(K, 0, flag_basis.nrows(), sparse=True)
	
		M = matrix(QQ, list(rows), sparse=True) * flag_basis.T
		
		if M.rank() == 0:
			return matrix(QQ, 0, flag_basis.nrows(), sparse=True)
		
		M = M.echelon_form()
		M = M[:M.rank(),:]

		return M


class UnbalancedBlowupConstruction(Construction):


	def __init__(self, g, weights=None, field=None):
	
		if g.oriented:
			raise NotImplementedException("oriented graphs not supported.")
		
		self._graph = g
		
		if weights is None:
			self._weights = [Integer(1)] * g.n
		else:
			if len(weights) != g.n:
				raise ValueError
			self._weights = weights
	
		if field is None:
			self._field = RationalField()
		else:
			self._field = field
	
		
	def edge_density(self):
	
		den_pairs = self.subgraph_densities(self._graph.r)

		for pair in den_pairs:
			g, den = pair
			if g.ne == 1:
				return den
	
		
	def subgraph_densities(self, n):

		cn = self._graph.n
		total = Integer(0)
		sharp_graph_counts = {}
		sharp_graphs = []

		for P in UnorderedTuples(range(1, cn + 1), n):
		
			factor = factorial(n)
			for i in range(1, cn + 1):
				factor /= factorial(P.count(i))

			for v in P:
				factor *= self._weights[v - 1]
			
			ig = self._graph.degenerate_induced_subgraph(P)
			ig.make_minimal_isomorph()
			
			ghash = hash(ig)
			if ghash in sharp_graph_counts:
				sharp_graph_counts[ghash] += factor
			else:
				sharp_graphs.append(ig)
				sharp_graph_counts[ghash] = factor

			total += factor
		
		return [(g, sharp_graph_counts[hash(g)] / total) for g in sharp_graphs]


	def k4(self):

		cn = self._graph.n

		x = polygen(QQ)
		expr = Integer(0)
		
		for tp in UnorderedTuples(range(1, cn + 1), 4):
			P = list(tp)
			
			ig = self._graph.degenerate_induced_subgraph(P)

			if ig.ne > 0:
				fact = Integer(1)
				for i in range(1, cn + 1):
					fact /= factorial(P.count(i))
				for i in P:
					if i < 5:
						fact *= x
					else:
						fact *= Integer(1)/4 - x
				expr += fact

		return expr
				


	def zero_eigenvectors(self, tg, flags, flag_basis=None):

		cn = self._graph.n
		s = tg.n
		k = flags[0].n # assume all flags the same order

		rows = []

		for tv in Tuples(range(1, cn + 1), s):

			it = self._graph.degenerate_induced_subgraph(tv)
			if not it.is_equal(tg):
				continue

			total = Integer(0)
			row = [0] * len(flags)
		
			for ov in UnorderedTuples(range(1, cn + 1), k - s):
		
				factor = factorial(k - s)
				for i in range(1, cn + 1):
					factor /= factorial(ov.count(i))

				for v in ov:
					factor *= self._weights[v - 1]
				
				ig = self._graph.degenerate_induced_subgraph(tv + ov)
				ig.t = s
				ig.make_minimal_isomorph()
				
				for j in range(len(flags)):
					if ig.is_equal(flags[j]):
						row[j] += factor
						total += factor
						break
						
			for j in range(len(flags)):
				row[j] /= total	
			rows.append(row)

		if flag_basis == None:
			flag_basis = identity_matrix(QQ, len(flags), sparse=True)

		if len(rows) == 0:
			return matrix(self._field, 0, flag_basis.nrows(), sparse=True)

		M = matrix(self._field, rows, sparse=True) * flag_basis.T
		
		if M.rank() == 0:
			return matrix(self._field, 0, flag_basis.nrows(), sparse=True)
		
		M = M.echelon_form()
		M = M[:M.rank(),:]

		return M
	