from datetime import datetime
import aiohttp
import asyncio


async def communicate(session, url, headers, post_data):
    async with session.post(url, headers=headers, json=post_data, ssl=False) as resp:
        response = await resp.json()
        return response

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i +n]


async def create_container(params):

    post_data = params['container_common']
    post_data['name'] = params['container_name']
    post_data['label'] = params['artifact_label']
    
    async with aiohttp.ClientSession() as session:
        
        tasks = []
        url = "{}container".format(params['base_url'])
        headers = params['headers']
        tasks.append(asyncio.ensure_future(communicate(session, url, headers, post_data)))
        
        responses = await asyncio.gather(*tasks)
        response = responses[0]
        #print(response)
        
        if response.get('success'):
            #print("Phantom Response:")
            #print(response)
            return response
        else:
            return response

async def add_artifacts(params, artifacts):
    
    post_data = []

    for artifact in artifacts:
        items = {}
        items['container_id'] = params['container_id']
        items['label'] = params['artifact_label']
        items['name'] = 'artifact: {}'.format(list(artifact.values())[0])
        items['cef'] = artifact
        post_data.append(items)
    
    for pd in post_data[:-1]:
        pd['run_automation'] = False
    
    post_data[-1]['run_automation'] = True

    post_data_chunks = chunks(post_data, 10)

    #print(list(post_data_chunks))
    

    async with aiohttp.ClientSession() as session:
        tasks = []
        url = "{}artifact".format(params['base_url'])
        headers=params['headers']
        #for pd in post_data_chunks:
        tasks.append(asyncio.ensure_future(communicate(session, url, headers, post_data)))

        response = await asyncio.gather(*tasks)
        return response



def process(data):

    dtg = datetime.now().strftime("%Y%m%d_%H%M")
    params = data['args']
    artifacts = data['cef_formatted']
    username = params['username']
    
    params['container_common'] = {"description" : "Submitted by: {}".format(username)}
    params['base_url'] = 'https://{}/rest/'.format(params['phantom_server'])
    params['container_name'] = dtg
    #print(params['container_name'])
    params['headers'] = {"ph-auth-token": params['token']}
    
    #if data['dev']:
        #params['container_id'] = 999
        #pass
    #else:
    container_response = asyncio.run(create_container(params))
        #params['container_data'] = container_response
    #params['container_id'] = container_response[0].get('id')
    ## TODO: handle success = false response from Phantom Server
    if container_response.get('success'):
        #print("GOT SUCCESS, PROCEED")
        params['container_id'] = container_response.get('id')
    
        if params['container_id']:
            artifacts_response = asyncio.run(add_artifacts(params, artifacts))
    

        rfi_id = '{}{}_{}'.format(params['artifact_label'], dtg[:8], params['container_id'])
        summary = []
        summary.append('RFI ID: {}'.format(rfi_id))
        summary.append('Container Name: {}'.format(params['container_name']))
        summary.append('Container ID: {}'.format(params['container_id']))

        responses = {}
        responses['container_response'] = container_response
        responses['artifacts_response'] = artifacts_response
        responses['summary'] = summary
        return responses

    else:
        return 