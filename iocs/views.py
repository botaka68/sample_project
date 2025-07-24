from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UploadFileForm, SubmitIndicatorsForm
from django.http import HttpResponseRedirect
import os
import iocs.formatcat as formatcat
import iocs.bulkcat as bulkcat
from django.contrib import messages
from accounts.models import Organization



def handle_upload(f):
    upload_file = os.path.join(settings.MEDIA_ROOT, f.name)
    with open(upload_file, 'wb+') as artifact_file:
        for chunk in f.chunks():
            artifact_file.write(chunk)
    

@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            
            handle_upload(request.FILES['file'])
            artifact_file = os.path.join(settings.MEDIA_ROOT, request.FILES['file'].name)
            
            with open(artifact_file, 'r') as file:
                artifacts = file.read().splitlines()
            
            os.remove(artifact_file)
            # remove whitespace chars
            artifacts = list(map(str.strip, artifacts))

            # Remove empty lines/strings
            artifacts = list(filter(None, artifacts)) 

            output = formatcat.run(artifacts)
            output['dev'] = False
            #print("OUTPUT")
            #print(output)
    
            try:
                del request.session['results']
            except KeyError:
                pass

            request.session['results'] = output
            request.session['source'] = "upload"
            messages.success(request, f'Successfully processed: {request.FILES["file"].name}!   Press submit to continue.')
            
            return HttpResponseRedirect('/summary')
        else:
            messages.warning(request, 'Error occured processing file')
                        
    else:
        form = UploadFileForm()
        return render(request, 'iocs/upload.html', {'form': form})



@login_required
def summary(request):
    
    results = request.session['results']
    source = request.session['source']
    summary = []

    summary.append((f'Total Artifacts: {results["total_count"]}'))
    artifact_type_count = results['artifact_type_count']
    
    if 'ip' in artifact_type_count:
        summary.append(f'IP Addresses: {artifact_type_count["ip"]}')
    if 'domain' in artifact_type_count:
        summary.append(f'Domains: {artifact_type_count["domain"]}')
    if 'md5' in artifact_type_count:
        summary.append(f'MD5 Hashes: {artifact_type_count["md5"]}')
    if 'sha1' in artifact_type_count:
        summary.append(f'SHA1 Hashes: {artifact_type_count["sha1"]}')
    if 'sha256' in artifact_type_count:
        summary.append(f'SHA256 Hashes: {artifact_type_count["sha256"]}')
    
    try:
        summary.append(f"Invalid artifacts: {len(results['invalid_artifacts'])}")
        summary.append((f'Invalid Artifacts: {(", ").join(results["invalid_artifacts"])}'))
    except:
        pass

    #print(results)
    context = {'result_data': summary,  'source':  source}

    return render(request, 'iocs/summary.html', context)


@login_required
def success(request):
    
    args = {}
    results = request.session['results']
    
    if request.method == 'POST':
        user = request.user
        args['username'] = request.user.username
        user_org = user.org
        args['artifact_label'] = user_org
        org_queryset = Organization.objects.filter(organization=user_org)
        
        try:
            org = org_queryset.get()    
        except:
            org = None 
        
        if org:
            args['phantom_server'] = org.phantom_server
            args['token'] = org.auth_token

    
        results['args'] = args
        
        responses = bulkcat.process(results)
        #print("Success Responses, Yay")
        #print(responses)
        
        if responses:
            context = {'result_data': responses['summary']}
            return render(request, 'iocs/success.html', context)
        else:
            
            messages.warning(request, 'An unknown error has occured while connecting to the server. Artifacts were not submitted.')
            return HttpResponseRedirect('/error')  
    else:

        context = {'result_data': []}
        return render(request, 'iocs/success.html', context)


@login_required
def submit(request):

    if request.method == 'POST':
        form = SubmitIndicatorsForm(request.POST or None)

        if form.is_valid():
            
            indicators = form.cleaned_data['indicators'].splitlines()
            
            # remove whitespace chars
            indicators = list(map(str.strip, indicators))

            # Remove empty lines/strings
            indicators = list(filter(None, indicators)) 
            
            #print(indicators)

            output = formatcat.run(indicators)
            #output['dev'] = True
            #print("OUTPUT")
            #print(output)
    
            try:
                del request.session['results']
            except KeyError:
                pass

            request.session['results'] = output
            request.session['source'] = "submit"
            messages.success(request, 'Successfully processed indicators! Press submit to continue.')
            
            
            return HttpResponseRedirect('/summary')  

    else:
        form = SubmitIndicatorsForm()
        return render(request, 'iocs/submit.html', {'form': form})



@login_required
def error(request):
    

    return render(request, 'iocs/error.html')