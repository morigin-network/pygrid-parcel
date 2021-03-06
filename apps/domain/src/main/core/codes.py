class MSG_FIELD:
    REQUEST_ID = "request_id"
    TYPE = "type"
    DATA = "data"
    WORKER_ID = "worker_id"
    MODEL = "model"
    MODEL_ID = "model_id"
    ALIVE = "alive"
    ALLOW_DOWNLOAD = "allow_download"
    ALLOW_REMOTE_INFERENCE = "allow_remote_inference"
    MPC = "mpc"
    PROPERTIES = "model_properties"
    SIZE = "model_size"
    SYFT_VERSION = "syft_version"
    REQUIRES_SPEED_TEST = "requires_speed_test"
    USERNAME_FIELD = "username"
    PASSWORD_FIELD = "password"


class MODEL_CENTRIC_FL_EVENTS(object):
    HOST_FL_TRAINING = "model-centric/host-training"
    REPORT = "model-centric/report"
    AUTHENTICATE = "model-centric/authenticate"
    CYCLE_REQUEST = "model-centric/cycle-request"


class USER_EVENTS(object):
    GET_ALL_USERS = "list-users"
    GET_SPECIFIC_USER = "list-user"
    SEARCH_USERS = "search-users"
    PUT_EMAIL = "put-email"
    PUT_PASSWORD = "put-password"
    PUT_ROLE = "put-role"
    PUT_GROUPS = "put-groups"
    DELETE_USER = "delete-user"
    SIGNUP_USER = "signup-user"
    LOGIN_USER = "login-user"


class ROLE_EVENTS(object):
    CREATE_ROLE = "create-role"
    GET_ROLE = "get-role"
    GET_ALL_ROLES = "get-all-roles"
    PUT_ROLE = "put-role"
    DELETE_ROLE = "delete-role"


class GROUP_EVENTS(object):
    CREATE_GROUP = "create-group"
    GET_GROUP = "get-group"
    GET_ALL_GROUPS = "get-all-groups"
    PUT_GROUP = "put-group"
    DELETE_GROUP = "delete-group"


class RESPONSE_MSG(object):
    ERROR = "error"
    SUCCESS = "success"


class CYCLE(object):
    STATUS = "status"
    KEY = "request_key"
    PING = "ping"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    VERSION = "version"
    PLANS = "plans"
    PROTOCOLS = "protocols"
    CLIENT_CONFIG = "client_config"
    SERVER_CONFIG = "server_config"
    TIMEOUT = "timeout"
    DIFF = "diff"
    AVG_PLAN = "averaging_plan"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INFERENCE = "inference_plan"
