/* Presentation and navigation enhancements. The graph model stays in app.js. */
'use strict';
(() => {
  const titles = {
    graph:['KNOWLEDGE EXPLORER','图谱探索','从七类产业要素出发，探索层内与跨层的知识关联。'],
    industry:['INDUSTRY LANDSCAPE','产业全景','沿产业环节浏览行业结构，查看各领域的关联实体。'],
    records:['RELATIONSHIP EVIDENCE','关系溯源','让每条关联回到原始来源，核查时间与证据。'],
    directory:['ENTITY INDEX','实体索引','浏览七类产业实体，连接名称背后的产业知识。']
  };
  function disclosure(buttonId,panelId) {
    const button=document.getElementById(buttonId),panel=document.getElementById(panelId);
    button.onclick=()=>{panel.hidden=!panel.hidden;button.setAttribute('aria-expanded',String(!panel.hidden));};
  }
  disclosure('toggle-timeline','timeline-panel');
  disclosure('toggle-filters','advanced-filters');
  const help=$('help-dialog');
  $('open-help').onclick=()=>help.showModal();
  for(const id of ['close-help','help-start'])$(id).onclick=()=>help.close();
  help.addEventListener('click',event=>{if(event.target===help){const r=help.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)help.close();}});
  document.querySelector('.brand').onclick=e=>{e.preventDefault();setView('graph');window.scrollTo({top:0,behavior:'smooth'});};
  document.addEventListener('keydown',event=>{
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();$('global-search').focus();}
  });
  const tabButtons=[...document.querySelectorAll('.tabs [role="tab"]')];
  tabButtons.forEach((button,index)=>button.addEventListener('keydown',event=>{
    const vertical=window.innerWidth>760;
    const previous=vertical?'ArrowUp':'ArrowLeft',next=vertical?'ArrowDown':'ArrowRight';
    let target;
    if(event.key===previous)target=tabButtons[(index+tabButtons.length-1)%tabButtons.length];
    if(event.key===next)target=tabButtons[(index+1)%tabButtons.length];
    if(event.key==='Home')target=tabButtons[0];
    if(event.key==='End')target=tabButtons.at(-1);
    if(target){event.preventDefault();target.click();target.focus();}
  }));
  const layerIcon='<svg viewBox="0 0 48 48" fill="none" aria-hidden="true"><path d="m24 7 18 10-18 10L6 17 24 7Z" stroke="currentColor" stroke-width="1.8"/><path d="m7 24 17 10 17-10M7 31l17 10 17-10" stroke="currentColor" stroke-width="1.8"/></svg>';
  function emptyInspector(id,title,copy) {
    const el=$(id);
    if(el.children.length!==1||el.querySelector('.inspector-empty'))return;
    el.innerHTML=`<div class="inspector-eyebrow">DETAIL INSPECTOR</div><h2>${title}</h2><div class="inspector-empty"><div class="inspector-illustration">${layerIcon}</div><h3>让关联展开</h3><p>${copy}</p></div><div class="inspector-guide"><span>01</span><p>选择感兴趣的产业实体</p><span>02</span><p>浏览相关关系与时间</p><span>03</span><p>回到原文查看证据</p></div>`;
    if(id==='node-inspector') {
      const sample=DATA.nodes.find(n=>n.type==='Company'&&n.name==='中芯国际'&&snapshotIDs.has(n.id))||DATA.nodes.find(n=>n.type==='Company'&&snapshotIDs.has(n.id));
      if(sample){const b=document.createElement('button');b.className='example-button';b.textContent='探索示例：'+sample.name;b.onclick=()=>chooseNode(sample.id);el.append(b);}
    }
  }
  function refreshChrome() {
    const [kicker,title,subtitle]=titles[view]||titles.graph;
    document.querySelector('.workspace-intro .section-kicker').textContent=kicker;
    $('workspace-title').textContent=title;
    $('workspace-subtitle').textContent=subtitle;
    $('open-complete-industry-tree').hidden=view==='industry';
    tabButtons.forEach(button=>button.tabIndex=button.dataset.view===view?0:-1);
    document.querySelector('.tabs').setAttribute('aria-orientation',window.innerWidth>760?'vertical':'horizontal');
    const network=$('graph-mode').value==='network';
    for(const id of ['fit-network','zoom-in','zoom-out','focus-neighbors','clear-node']){
      $(id).disabled=!network;
      $(id).title=network?'':'在实体网络视图中使用';
    }
    $('download-graph').title='导出七类要素的结构总览图';
    $('scope-badge').textContent=fullTime?'全期图谱':$('date-from').value+' 至 '+$('date-to').value;
    $('time-filter-badge').hidden=fullTime;
    $('toggle-timeline').classList.toggle('has-filters',!fullTime);
    const active=[
      $('knowledge-snapshot').value!=='current',$('scope-filter').value!=='all',$('verification').value!=='all',
      !$('show-structure').checked,...['show-supplement','full-source-only','direct-only','include-planned'].map(id=>$(id).checked)
    ].filter(Boolean).length;
    $('active-filter-count').textContent=active;
    $('active-filter-count').hidden=!active;
    $('toggle-filters').classList.toggle('has-filters',!!active);
    $('snapshot-caption').textContent=$('knowledge-snapshot').value==='asof2025'?'知识截止 2025-12-31':'数据快照 '+modelDate;
    emptyInspector('node-inspector','实体详情','点击图层查看关联，或搜索一个企业，在实体网络中展开它的产业联系。');
    emptyInspector('industry-inspector','产业关联','在左侧选择一个行业，查看该领域的关联企业及其他产业要素。');
    emptyInspector('evidence-inspector','关系溯源','选择一条关系记录，查看原文证据、来源文档与两类时间信息。');
  }
  const originalSetView=setView;
  setView=function(next){originalSetView(next);refreshChrome();};
  const originalUpdate=update;
  update=function(){originalUpdate();refreshChrome();};
  const originalSwitch=switchGraphMode;
  switchGraphMode=function(){originalSwitch();refreshChrome();};
  // Existing handlers preserve their data operations; refresh only the surrounding UI.
  for(const id of ['graph-mode','knowledge-snapshot','scope-filter','verification','show-structure','show-supplement','full-source-only','direct-only','include-planned','time-axis','include-unknown','include-coarse'])$(id).addEventListener('change',refreshChrome);
  const headingObserver=new MutationObserver(()=>{
    for(const id of ['node-inspector','industry-inspector','evidence-inspector']){
      const el=$(id);el.classList.toggle('has-selection',!el.querySelector('.inspector-empty'));
    }
  });
  for(const id of ['node-inspector','industry-inspector','evidence-inspector'])headingObserver.observe($(id),{childList:true});
  $('global-search').addEventListener('input',()=>{
    if($('global-search').value.trim()&&!$('search-results').children.length){$('search-results').innerHTML='<div class="search-empty">暂无匹配实体，试试其他名称或别名。</div>';}
  });
  window.addEventListener('resize',()=>document.querySelector('.tabs').setAttribute('aria-orientation',window.innerWidth>760?'vertical':'horizontal'));
  refreshChrome();
})();
