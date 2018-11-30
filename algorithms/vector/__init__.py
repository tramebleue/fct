from DeduplicateLines import DeduplicateLines
from InterpolateLine import InterpolateLine
from JoinByNearest import JoinByNearest
from LineMidpoints import LineMidpoints
from MeasureDistanceToPointLayer import MeasureDistanceToPointLayer
from MergeGeometries import MergeGeometries
from PointOnSurface import PointOnSurface
from RandomPoints import RandomPoints
from RandomPoissonDiscSampling import RandomPoissonDiscSampling
from RegularHexPoints import RegularHexPoints
from RemoveSmallPolygonalObjects import RemoveSmallPolygonalObjects
from SafePolygonIntersection import SafePolygonIntersection
from SegmentEndpoints import SegmentEndpoints
from SelectByDistance import SelectByDistance
from SelectNearestFeature import SelectNearestFeature
from SplitLine import SplitLine
from SplitLineIntoSegments import SplitLineIntoSegments
from UniquePoints import UniquePoints
from UniqueValuesTable import UniqueValuesTable
from UpdateFieldByExpression import UpdateFieldByExpression
from UpdateFieldByExpressionInPlace import UpdateFieldByExpressionInPlace


def vectorAlgorithms():

    return [
        DeduplicateLines(),
        InterpolateLine(),
        JoinByNearest(),
        LineMidpoints(),
        MeasureDistanceToPointLayer(),
        MergeGeometries(),
        PointOnSurface(),
        RandomPoints(),
        RandomPoissonDiscSampling(),
        RegularHexPoints(),
        RemoveSmallPolygonalObjects(),
        SafePolygonIntersection(),
        SegmentEndpoints(),
        SelectByDistance(),
        SelectNearestFeature(),
        SplitLine(),
        SplitLineIntoSegments(),
        UniquePoints(),
        UniqueValuesTable(),
        UpdateFieldByExpression(),
        UpdateFieldByExpressionInPlace()
    ]