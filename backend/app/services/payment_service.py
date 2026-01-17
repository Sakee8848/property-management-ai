"""
支付服务 - 集成微信支付和支付宝
"""
from typing import Dict, Optional
from datetime import datetime
from wechatpy.pay import WeChatPay
from alipay import AliPay
from loguru import logger

from app.core.config import settings


class PaymentService:
    """支付服务类"""
    
    def __init__(self):
        # 微信支付
        if settings.WECHAT_PAY_APPID and settings.WECHAT_PAY_MCH_ID:
            self.wechat_pay = WeChatPay(
                appid=settings.WECHAT_PAY_APPID,
                api_key=settings.WECHAT_PAY_API_KEY,
                mch_id=settings.WECHAT_PAY_MCH_ID,
            )
        else:
            self.wechat_pay = None
        
        # 支付宝
        if settings.ALIPAY_APPID and settings.ALIPAY_PRIVATE_KEY:
            self.alipay = AliPay(
                appid=settings.ALIPAY_APPID,
                app_notify_url=None,
                app_private_key_string=settings.ALIPAY_PRIVATE_KEY,
                alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY,
                sign_type="RSA2",
            )
        else:
            self.alipay = None
    
    async def create_wechat_order(
        self,
        bill_number: str,
        amount: float,
        description: str,
        user_openid: str
    ) -> Dict:
        """
        创建微信支付订单
        
        Args:
            bill_number: 账单号
            amount: 金额(元)
            description: 订单描述
            user_openid: 用户openid
        
        Returns:
            支付参数
        """
        if not self.wechat_pay:
            raise Exception("微信支付未配置")
        
        try:
            # 金额转换为分
            total_fee = int(amount * 100)
            
            # 调用统一下单接口
            result = self.wechat_pay.order.create(
                trade_type='JSAPI',
                body=description,
                out_trade_no=bill_number,
                total_fee=total_fee,
                notify_url=f"{settings.API_PREFIX}/payments/wechat/notify",
                user_id=user_openid,
            )
            
            # 生成JSAPI支付参数
            pay_params = self.wechat_pay.jsapi.get_jsapi_params(
                prepay_id=result['prepay_id']
            )
            
            return {
                "success": True,
                "payment_params": pay_params,
                "prepay_id": result['prepay_id']
            }
        
        except Exception as e:
            logger.error(f"创建微信订单错误: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_alipay_order(
        self,
        bill_number: str,
        amount: float,
        description: str,
        return_url: Optional[str] = None
    ) -> Dict:
        """
        创建支付宝订单
        
        Args:
            bill_number: 账单号
            amount: 金额(元)
            description: 订单描述
            return_url: 支付完成返回URL
        
        Returns:
            支付URL
        """
        if not self.alipay:
            raise Exception("支付宝未配置")
        
        try:
            # 调用支付宝H5支付接口
            order_string = self.alipay.api_alipay_trade_wap_pay(
                out_trade_no=bill_number,
                total_amount=amount,
                subject=description,
                return_url=return_url or f"{settings.API_PREFIX}/payments/alipay/return",
                notify_url=f"{settings.API_PREFIX}/payments/alipay/notify"
            )
            
            # 生成支付URL
            payment_url = f"https://openapi.alipay.com/gateway.do?{order_string}"
            
            return {
                "success": True,
                "payment_url": payment_url
            }
        
        except Exception as e:
            logger.error(f"创建支付宝订单错误: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_wechat_callback(self, data: Dict) -> Dict:
        """验证微信支付回调"""
        if not self.wechat_pay:
            return {"success": False, "error": "微信支付未配置"}
        
        try:
            # 验证签名
            if not self.wechat_pay.check_signature(data):
                return {"success": False, "error": "签名验证失败"}
            
            # 解析数据
            result = {
                "success": data.get('result_code') == 'SUCCESS',
                "transaction_id": data.get('transaction_id'),
                "out_trade_no": data.get('out_trade_no'),
                "total_fee": int(data.get('total_fee', 0)) / 100,
            }
            
            return result
        
        except Exception as e:
            logger.error(f"验证微信回调错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def verify_alipay_callback(self, data: Dict) -> Dict:
        """验证支付宝回调"""
        if not self.alipay:
            return {"success": False, "error": "支付宝未配置"}
        
        try:
            # 验证签名
            signature = data.pop('sign')
            if not self.alipay.verify(data, signature):
                return {"success": False, "error": "签名验证失败"}
            
            # 解析数据
            result = {
                "success": data.get('trade_status') in ['TRADE_SUCCESS', 'TRADE_FINISHED'],
                "transaction_id": data.get('trade_no'),
                "out_trade_no": data.get('out_trade_no'),
                "total_fee": float(data.get('total_amount', 0)),
            }
            
            return result
        
        except Exception as e:
            logger.error(f"验证支付宝回调错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def query_order(self, transaction_id: str, payment_method: str) -> Dict:
        """
        查询订单状态
        
        Args:
            transaction_id: 交易号
            payment_method: 支付方式(wechat/alipay)
        
        Returns:
            订单信息
        """
        try:
            if payment_method == 'wechat' and self.wechat_pay:
                result = self.wechat_pay.order.query(transaction_id=transaction_id)
                return {
                    "success": True,
                    "trade_state": result.get('trade_state'),
                    "paid": result.get('trade_state') == 'SUCCESS'
                }
            
            elif payment_method == 'alipay' and self.alipay:
                result = self.alipay.api_alipay_trade_query(out_trade_no=transaction_id)
                return {
                    "success": True,
                    "trade_state": result.get('trade_status'),
                    "paid": result.get('trade_status') in ['TRADE_SUCCESS', 'TRADE_FINISHED']
                }
            
            else:
                return {"success": False, "error": "不支持的支付方式"}
        
        except Exception as e:
            logger.error(f"查询订单错误: {str(e)}")
            return {"success": False, "error": str(e)}
