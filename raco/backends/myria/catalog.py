from raco.catalog import Catalog
import raco.scheme as scheme
from raco.representation import RepresentationProperties
from raco.expression import UnnamedAttributeRef as AttIndex
from .errors import MyriaError


class MyriaCatalog(Catalog):

    def __init__(self, connection):
        self.connection = connection

    def get_scheme(self, rel_key):
        relation_args = {
            'userName': rel_key.user,
            'programName': rel_key.program,
            'relationName': rel_key.relation
        }
        if not self.connection:
            raise RuntimeError(
                "no schema for relation %s because no connection" % rel_key)
        try:
            dataset_info = self.connection.dataset(relation_args)
        except MyriaError:
            raise ValueError('No relation {} in the catalog'.format(rel_key))
        schema = dataset_info['schema']
        return scheme.Scheme(zip(schema['columnNames'], schema['columnTypes']))

    def get_num_servers(self):
        if not self.connection:
            raise RuntimeError("no connection.")
        return len(self.connection.workers_alive())

    def num_tuples(self, rel_key):
        relation_args = {
            'userName': rel_key.user,
            'programName': rel_key.program,
            'relationName': rel_key.relation
        }
        if not self.connection:
            raise RuntimeError(
                "no cardinality of %s because no connection" % rel_key)
        try:
            dataset_info = self.connection.dataset(relation_args)
        except MyriaError:
            raise ValueError(rel_key)
        num_tuples = dataset_info['numTuples']
        assert isinstance(num_tuples, (int, long)), type(num_tuples)
        # that's a work round. numTuples is -1 if the dataset is old
        if num_tuples != -1:
            assert num_tuples >= 0
            return num_tuples
        return DEFAULT_CARDINALITY

    def partitioning(self, rel_key):
        relation_args = {
            'userName': rel_key.user,
            'programName': rel_key.program,
            'relationName': rel_key.relation
        }
        if not self.connection:
            raise RuntimeError(
                "no schema for relation %s because no connection" % rel_key)
        try:
            dataset_info = self.connection.dataset(relation_args)
        except MyriaError:
            raise ValueError('No relation {} in the catalog'.format(rel_key))
        partition_function = dataset_info['howPartitioned']['pf']
        # TODO: can we do anything useful with other hash partition functions?
        if partition_function and partition_function['type'] in [
                "SingleFieldHash", "MultiFieldHash"]:
            if partition_function['type'] == "SingleFieldHash":
                indexes = [partition_function['index']]
            else:
                indexes = partition_function['indexes']
            return RepresentationProperties(
                hash_partitioned=frozenset(AttIndex(i) for i in indexes))
        return RepresentationProperties()
