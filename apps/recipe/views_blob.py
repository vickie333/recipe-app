# apps/recipe/views_blob.py
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

BLOB_READ_WRITE_TOKEN = getattr(settings, 'BLOB_READ_WRITE_TOKEN', None)
VERCEL_BLOB_API = "https://blob.vercel-storage.com"

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_blob_upload(request):
    """
    Server-side upload to Vercel Blob Storage.
    Client sends file in 'file' field.
    
    Returns:
        - url: Public URL to access the blob
        - downloadUrl: URL that forces download
        - pathname: Path in blob storage
        - contentType: MIME type
        - contentDisposition: inline or attachment
    """
    if not BLOB_READ_WRITE_TOKEN:
        return Response(
            {"error": "BLOB_READ_WRITE_TOKEN not configured on server"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if 'file' not in request.FILES:
        return Response(
            {"error": "No file provided. Send file in 'file' field."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    file_obj = request.FILES['file']
    filename = file_obj.name
    content_type = file_obj.content_type or 'application/octet-stream'

    # Construct URL for upload
    # Using addRandomSuffix parameter to avoid filename conflicts
    upload_url = f"{VERCEL_BLOB_API}/{filename}"

    headers = {
        "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        "x-api-version": "7",
        "x-content-type": content_type,
        "x-add-random-suffix": "1"  # Prevents overwriting existing files
    }

    try:
        # Read file content
        file_content = file_obj.read()
        
        # Upload to Vercel Blob
        response = requests.put(
            upload_url, 
            data=file_content, 
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        response.raise_for_status()
        
        # Return the blob metadata
        blob_data = response.json()
        
        return Response({
            "success": True,
            "blob": blob_data,
            "message": f"File '{filename}' uploaded successfully"
        }, status=status.HTTP_201_CREATED)
        
    except requests.exceptions.Timeout:
        return Response(
            {"error": "Upload timeout - file too large or connection slow"}, 
            status=status.HTTP_408_REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = error_detail.get('error', {}).get('message', error_msg)
            except ValueError:
                error_msg = e.response.text or error_msg
        
        return Response(
            {"error": f"Upload failed: {error_msg}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_blobs(request):
    """
    List all blobs in the storage.
    Supports pagination with cursor.
    
    Query parameters:
        - cursor: Pagination cursor (optional)
        - limit: Number of items (1-1000, default 10)
        - prefix: Filter by prefix (optional)
    """
    if not BLOB_READ_WRITE_TOKEN:
        return Response(
            {"error": "BLOB_READ_WRITE_TOKEN not configured"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    cursor = request.query_params.get('cursor', None)
    limit = int(request.query_params.get('limit', 10))
    prefix = request.query_params.get('prefix', '')

    list_url = f"{VERCEL_BLOB_API}/"
    
    headers = {
        "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        "x-api-version": "7"
    }
    
    params = {
        "limit": min(limit, 1000)  # Max 1000
    }
    
    if cursor:
        params['cursor'] = cursor
    if prefix:
        params['prefix'] = prefix

    try:
        response = requests.get(list_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return Response(response.json())
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_msg = e.response.json()
            except ValueError:
                error_msg = e.response.text
        return Response(
            {"error": error_msg}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_blob(request):
    """
    Delete a blob by URL.
    
    Request body:
        {"url": "https://xxxx.public.blob.vercel-storage.com/file.jpg"}
    """
    if not BLOB_READ_WRITE_TOKEN:
        return Response(
            {"error": "BLOB_READ_WRITE_TOKEN not configured"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    blob_url = request.data.get('url')
    if not blob_url:
        return Response(
            {"error": "Blob URL required in request body"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    headers = {
        "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        "x-api-version": "7"
    }

    try:
        response = requests.delete(blob_url, headers=headers, timeout=10)
        response.raise_for_status()
        return Response(
            {"success": True, "message": "Blob deleted successfully"}, 
            status=status.HTTP_200_OK
        )
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_msg = e.response.json()
            except ValueError:
                error_msg = e.response.text
        return Response(
            {"error": error_msg}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generate_upload_url(request):
    """
    Generate a presigned URL for client-side uploads.
    This allows the client to upload directly to Vercel Blob
    without going through your Django server (saves bandwidth).
    
    Request body:
        {
            "filename": "myfile.jpg",
            "contentType": "image/jpeg"
        }
    
    Returns:
        {
            "uploadUrl": "https://...",
            "headers": {...},
            "method": "PUT"
        }
    """
    if not BLOB_READ_WRITE_TOKEN:
        return Response(
            {"error": "BLOB_READ_WRITE_TOKEN not configured"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    filename = request.data.get('filename')
    content_type = request.data.get('contentType', 'application/octet-stream')
    
    if not filename:
        return Response(
            {"error": "filename required in request body"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate upload URL
    upload_url = f"{VERCEL_BLOB_API}/{filename}"
    
    headers = {
        "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        "x-api-version": "7",
        "x-content-type": content_type,
        "x-add-random-suffix": "1"
    }
    
    return Response({
        "uploadUrl": upload_url,
        "headers": headers,
        "method": "PUT",
        "instructions": "Use PUT request with file binary data and the provided headers"
    })