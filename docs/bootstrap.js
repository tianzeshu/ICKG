'use strict';
(async()=>{
const status=document.getElementById('loading-status');
try{
const response=await fetch('./graph-source.html');
if(!response.ok)throw Error('图谱数据请求失败（'+response.status+'）');
const source=await response.text();
const match=source.match(/<script id="graph-data" type="application\/json">([\s\S]*?)<\/script>/);
if(!match)throw Error('未找到图谱数据');
const payload=document.createElement('script');payload.id='graph-data';payload.type='application/json';payload.textContent=match[1];document.body.append(payload);
for(const name of ['app.js','ui.js'])await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=name;script.onload=resolve;script.onerror=()=>reject(Error('界面资源载入失败'));document.body.append(script);});
if(!document.getElementById('metric-nodes').textContent.match(/[0-9]/))throw Error('图谱初始化未完成');
status.remove();
}catch(error){
status.replaceChildren();status.classList.add('load-error');
const text=document.createElement('span');text.textContent='图谱暂未载入。'+(location.protocol==='file:'?'请使用随附的单文件预览，或通过网页服务打开。':'请检查网络后重试。');
const retry=document.createElement('button');retry.textContent='重新载入';retry.onclick=()=>location.reload();status.append(text,retry);console.error(error);
}
})();
