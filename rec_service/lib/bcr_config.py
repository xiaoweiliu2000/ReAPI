'''
    1. common config
'''
GLOBAL_DEVICE = 'cpu'   # 使用cpu或cuda
CONCURRENCY_NUM = 12    # Flask的并发进程数量 
LOG_PATH = './logs/bcr_backend_service.log'

'''
    2. config cache paths 
    bcr_backend
'''
MODEL_ROOT_PATH = './models/'
MODEL_PATHS = { # 模型路径
    'bilateral' : MODEL_ROOT_PATH + 'model_bilateral.bin', 
    'mashup' : MODEL_ROOT_PATH + 'model_mashup.bin', 
    'api' : MODEL_ROOT_PATH + 'model_api.bin'
    }
DICT_PATH = MODEL_ROOT_PATH + 'dataDict.bin' # 数据字典路径
DATASET_PATHs = { # 数据库路径
    'apiData' : './data/apiData.json',
    'mashupData' : './data/mashupData.json'
}
DATASET_BIN_PATHs = { # 处理后的数据路径
    'apiData' : MODEL_ROOT_PATH + 'apiData.bin',
    'mashupData' : MODEL_ROOT_PATH + 'mashupData.bin'
}
PRE_ENCODING_PATH = MODEL_ROOT_PATH + 'apiEncodingDict.bin'

'''
    3. config model training data
    bcr_core
'''
DATA_HOME = '/home/weixiao/data/code/OCAR/data/'
featDict = {
    'mashup' : {
        'oneHot' : ['MashupId', 'MashupCategory', 'MashupType'],
        'multiHot' : ['MashupTags'],
        'text' : ['MashupDescription'],
        'dense' : ['MashupCC']
    },
    'api' : {
        'oneHot' : ['ApiId', 'ApiCategory', 'ApiProvider', 'ApiSSLSupport', 'ApiAuthModel', 'ApiNonProprietary', 'ApiScope', 'ApiDeviceSpecific', 'ApiArchitecture', 'ApiUnofficial', 'ApiHypermedia', 'ApiRestrictedAccess'],
        'multiHot' : ['ApiTags'],
        'text' : ['ApiDescription'],
        'dense' : ['ApiCC'],  # 仅目标API有
    }
}

featTable = {} 
featTable['mashup'] = {
    "Id":"MashupId",
    "Name":"MashupName",
    "TagList":"MashupTags",
    "Category":"MashupCategory",
    "Description":"MashupDescription",
    "Submitted Date":"MashupSubDate",
    "Url":"MashupUrl",
    "Company":"MashupCompany",
    "Type":"MashupType",
    "FollowerNum":"MashupFollowerNum",
    "APIs":"MashupRelatedAPIs"
}
featTable['api'] = {
    "Id":"ApiId",
    "Name":"ApiName",
    "TagList":"ApiTags",
    "Primary Category":"ApiCategory",
    "Description":"ApiDescription",
    "FollowerNum":"ApiFollowerNum",
    "API Endpoint":"ApiEndpoint",
    "API Portal / Home Page":"ApiHome",
    "Version status":"ApiVersionStatus",
    "Terms Of Service URL":"ApiTermsOfServiceUrl",
    "Is the API Design/Description Non-Proprietary ?":"ApiNonProprietary",
    "Scope":"ApiScope",
    "Device Specific":"ApiDeviceSpecific",
    "Docs Home Page URL":"ApiDocsHome",
    "Architectural Style":"ApiArchitecture",
    "Supported Request Formats":"ApiRequestFormats",
    "Supported Response Formats":"ApiResponseFormats",
    "Is This an Unofficial API?":"ApiUnofficial",
    "Is This a Hypermedia API?":"ApiHypermedia",
    "Restricted Access ( Requires Provider Approval )":"ApiRestrictedAccess",
    "SSL Support":"ApiSSLSupport",
    "API Forum / Message Boards":"ApiForum",
    "Support Email Address":"ApiSupportEmail",
    "Developer Support URL":"ApiDeveloperSupportURL",
    "API Provider":"ApiProvider",
    "Twitter URL":"ApiTwitterURL",
    "Authentication Model":"ApiAuthModel",
    "Type":"ApiType",
    "Version":"ApiVersion",
    "Description File URL":"ApiDescriptionFileURL",
    "Description File Type":"ApiDescriptionFileType",
    "How is this API different ?":"ApiHowDifferent",
    "Is the API related to anyother API ?":"ApiRelated2AnyotherAPI",
    "Interactive Console URL":"ApiInteractiveConsoleUrl",
    "Developer Home Page":"ApiDeveloperHome",
    "Type of License":"ApiTypeOfLicense",
    "Streaming Technology":"ApiStreamingTechnology",
    "Streaming Directions":"ApiStreamingDirections",
    "Direction Selection":"ApiDirectionSelection"
}

