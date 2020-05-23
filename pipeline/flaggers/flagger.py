import abc
from collections import namedtuple
from enum import IntEnum, auto

class Flags(IntEnum):
  ###################################################
  # Documentation of flags can be found in flags.md
  ###################################################

  #Null flags
  ROW_ID_NULL = auto()
  SERVICE_DATE_NULL = auto()
  VEHICLE_NUMBER_NULL = auto()
  LEAVE_TIME_NULL = auto()
  TRAIN_NULL = auto()
  ROUTE_NUMBER_NULL = auto()
  DIRECTION_NULL = auto()
  SERVICE_KEY_NULL = auto()
  TRIP_NUMBER_NULL = auto()
  STOP_TIME_NULL = auto()
  ARRIVE_TIME_NULL = auto()
  DWELL_NULL = auto()
  LOCATION_ID_NULL = auto()
  DOOR_NULL = auto()
  ONS_NULL = auto()
  OFFS_NULL = auto()
  ESTIMATED_LOAD_NULL = auto()
  LIFT_NULL = auto()
  MAXIMUM_SPEED_NULL = auto()
  TRAIN_MILEAGE_NULL = auto()
  PATTERN_DISTANCE_NULL = auto()
  LOCATION_DISTANCE_NULL = auto()
  X_COORDINATE_NULL = auto()
  Y_COORDINATE_NULL = auto()
  DATA_SOURCE_NULL = auto()
  SCHEDULE_STATUS_NULL = auto()
  TRIP_ID_NULL = auto()

  #Unobserved stop flag
  UNOBSERVED_STOP = auto()

  #Unopened door flag
  UNOPENED_DOOR = auto()

  #Duplicate flag
  DUPLICATE = auto()

class Flagger(abc.ABC):
  # Name must be overwritten
  @property
  def name(self):
    raise NotImplementedError

  @abc.abstractmethod
  def flag(self, data):
    # Child classes must return a lit of flags.
    pass


FlagInfo = namedtuple("FlagInfo", "name desc")

flag_descriptions = {
  Flags.ROW_ID_NULL: FlagInfo("null-row-id", "ROW_ID_NULL"),
  Flags.SERVICE_DATE_NULL: FlagInfo("null-service-date", "SERVICE_DATE_NULL"),
  Flags.VEHICLE_NUMBER_NULL: FlagInfo("null-vehicle-number", "VEHICLE_NUMBER_NULL"),
  Flags.LEAVE_TIME_NULL: FlagInfo("null-leave-time", "LEAVE_TIME_NULL"),
  Flags.TRAIN_NULL: FlagInfo("null-train", "TRAIN_NULL"),
  Flags.ROUTE_NUMBER_NULL: FlagInfo("null-route-number", "ROUTE_NUMBER_NULL"),
  Flags.DIRECTION_NULL: FlagInfo("null-direction", "DIRECTION_NULL"),
  Flags.SERVICE_KEY_NULL: FlagInfo("null-service-key", "SERVICE_KEY_NULL"),
  Flags.TRIP_NUMBER_NULL: FlagInfo("null-trip-number", "TRIP_NUMBER_NULL"),
  Flags.STOP_TIME_NULL: FlagInfo("null-stop-time", "STOP_TIME_NULL"),
  Flags.ARRIVE_TIME_NULL: FlagInfo("null-arrive-time", "ARRIVE_TIME_NULL"),
  Flags.DWELL_NULL: FlagInfo("null-dwell-time", "DWELL_NULL"),
  Flags.LOCATION_ID_NULL: FlagInfo("null-location-id", "LOCATION_ID_NULL"),
  Flags.DOOR_NULL: FlagInfo("null-door", "DOOR_NULL"),
  Flags.ONS_NULL: FlagInfo("null-ons", "ONS_NULL"),
  Flags.OFFS_NULL: FlagInfo("null-offs", "OFFS_NULL"),
  Flags.ESTIMATED_LOAD_NULL: FlagInfo("null-estimated-load", "ESTIMATED_LOAD_NULL"),
  Flags.LIFT_NULL: FlagInfo("null-lift", "LIFT_NULL"),
  Flags.MAXIMUM_SPEED_NULL: FlagInfo("null-maximum-speed", "MAXIMUM_SPEED_NULL"),
  Flags.TRAIN_MILEAGE_NULL: FlagInfo("null-train-mileage", "TRAIN_MILEAGE_NULL"),
  Flags.PATTERN_DISTANCE_NULL: FlagInfo("null-pattern-distance", "PATTERN_DISTANCE_NULL"),
  Flags.LOCATION_DISTANCE_NULL: FlagInfo("null-location-distance", "LOCATION_DISTANCE_NULL"),
  Flags.X_COORDINATE_NULL: FlagInfo("null-x-coordinate", "X_COORDINATE_NULL"),
  Flags.Y_COORDINATE_NULL: FlagInfo("null-y-coordinate", "Y_COORDINATE_NULL"),
  Flags.DATA_SOURCE_NULL: FlagInfo("null-data-source", "DATA_SOURCE_NULL"),
  Flags.SCHEDULE_STATUS_NULL: FlagInfo("null-schedule-status", "SCHEDULE_STATUS_NULL"),
  Flags.TRIP_ID_NULL: FlagInfo("null-trip-id", "TRIP_ID_NULL"),
  Flags.UNOBSERVED_STOP: FlagInfo("unobserved-stop", "UNOBSERVED_STOP"),
  Flags.UNOPENED_DOOR: FlagInfo("unopened-door", "UNOPENED_DOOR"),
  Flags.DUPLICATE: FlagInfo("duplicate", "DUPLICATE"),
}

flaggers = []
