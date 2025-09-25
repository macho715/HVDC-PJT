#!/usr/bin/env python3
"""
간단한 AWS MCP 서버
Claude Desktop과 AWS 서비스 연동을 위한 기본 MCP 서버
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP 서버 인스턴스 생성
server = Server("aws-mcp-server")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """사용 가능한 AWS 도구 목록 반환"""
    return [
        Tool(
            name="aws_list_s3_buckets",
            description="S3 버킷 목록 조회",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="aws_get_account_info",
            description="AWS 계정 정보 조회",
            inputSchema={
                "type": "object", 
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="aws_list_regions",
            description="AWS 리전 목록 조회",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """도구 호출 처리"""
    try:
        if name == "aws_list_s3_buckets":
            return await list_s3_buckets()
        elif name == "aws_get_account_info":
            return await get_account_info()
        elif name == "aws_list_regions":
            return await list_regions()
        else:
            return [TextContent(
                type="text",
                text=f"알 수 없는 도구: {name}"
            )]
    except Exception as e:
        logger.error(f"도구 실행 오류: {e}")
        return [TextContent(
            type="text",
            text=f"오류 발생: {str(e)}"
        )]

async def list_s3_buckets() -> List[TextContent]:
    """S3 버킷 목록 조회"""
    try:
        import boto3
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        
        buckets = []
        for bucket in response['Buckets']:
            buckets.append({
                'Name': bucket['Name'],
                'CreationDate': bucket['CreationDate'].isoformat()
            })
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "buckets": buckets,
                "count": len(buckets)
            }, indent=2, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"S3 버킷 조회 오류: {str(e)}"
        )]

async def get_account_info() -> List[TextContent]:
    """AWS 계정 정보 조회"""
    try:
        import boto3
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "account_info": response
            }, indent=2, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"계정 정보 조회 오류: {str(e)}"
        )]

async def list_regions() -> List[TextContent]:
    """AWS 리전 목록 조회"""
    try:
        import boto3
        ec2 = boto3.client('ec2')
        response = ec2.describe_regions()
        
        regions = []
        for region in response['Regions']:
            regions.append({
                'RegionName': region['RegionName'],
                'Endpoint': region['Endpoint']
            })
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "regions": regions,
                "count": len(regions)
            }, indent=2, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"리전 조회 오류: {str(e)}"
        )]

async def main():
    """메인 함수"""
    logger.info("AWS MCP 서버 시작...")
    
    # 환경 변수에서 AWS 설정 확인
    import os
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    logger.info(f"AWS Region: {aws_region}")
    logger.info(f"AWS Access Key: {aws_access_key[:8] if aws_access_key else 'Not set'}...")
    
    # stdio 서버 실행
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
