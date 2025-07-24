# just testing things out
import re




def dedupe_artifacts(artifacts):

    deduped_artifacts = {}
    # lowercase all elements of the list
    lower = [artifact.lower() for artifact in artifacts]
    deduped = list(set(lower))
    deduped_artifacts['deduped'] = deduped
    deduped_artifacts['duplicates_count'] =  len(artifacts) - len(deduped)
    return deduped_artifacts


def validate_artifacts(artifact):

    valid_ip = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
    valid_md5 = re.compile(r'(?=(\b[A-Fa-f0-9]{32}\b))')
    valid_sha1 = re.compile(r'(?=(\b[A-Fa-f0-9]{40}\b))')
    valid_sha256 = re.compile(r'(?=(\b[A-Fa-f0-9]{64}\b))')
    valid_domain = re.compile(
        r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )

    if valid_ip.match(artifact):
        return "ip"
    if valid_domain.match(artifact):
        return "domain"
    if valid_md5.match(artifact):
        return "md5"
    if valid_sha1.match(artifact):
        return "sha1"
    if valid_sha256.match(artifact):
        return("sha256")
    else:
        return 'invalid'


def cef_format(artifacts):
    
    cef_types = {
        'ip': 'sourceAddress', 
        'domain': 'destinationDnsDomain', 
        'md5': 'fileHash',
        'sha1': 'fileHash',
        'sha256': 'fileHash'
        }
    
    cef_formatted = []

    for artifact_type in artifacts:
        for artifact in artifacts[artifact_type]:
            cef_formatted.append({cef_types[artifact_type]: artifact})
    
    return cef_formatted


def artifact_count(artifacts):

    artifact_count = {}

    for artifact in artifacts:
        artifact_count[artifact] = len(artifacts[artifact])
    
    return artifact_count


def run(artifacts):
    # accepts a list of artifacts (ip, domain, hashes etc..) and processes for submition to phantom in cef format
    # returns additional metadata
    
    artifact_data = {}
    artifact_types = {}
    deduped = dedupe_artifacts(artifacts)

    for artifact in deduped['deduped']:
        valid_type = validate_artifacts(artifact)
        if valid_type not in artifact_types:
            artifact_types[valid_type] = []    
        artifact_types[valid_type].append(artifact)

    type_count = artifact_count(artifact_types)
    invalid_artifacts = artifact_types.pop('invalid', None)
    cef_formatted = cef_format(artifact_types)
    total_count = len(cef_formatted)
    
    artifact_data['artifact_type_count'] = type_count
    artifact_data['total_count'] = total_count
    artifact_data['duplicates_count'] = deduped['duplicates_count']
    artifact_data['invalid_artifacts'] = invalid_artifacts
    artifact_data['cef_formatted'] = cef_formatted
    
    return artifact_data




'''
sample = ['192.168.1.1','google.com', 'microsoft.com', 'something', 'GOOGLE.COM', 'bfc110c05c80b007f2e07386f1a454f0', '95405a8cf3c8bce435a43e615782088f0823d97afe1f0db19f4782322783d503', 'b41fb39f22d2ee9c42cb790b9b031e04a55f0465' ] 
data = process_artifacts(sample)
print(data)
'''