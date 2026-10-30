"""Transparent normalization rules for an independent sourced parts catalog."""
import re,unicodedata
def clean(x):return unicodedata.normalize('NFKC',str(x or '')).strip()
def maker_key(x):return ''.join(c for c in clean(x).casefold() if c.isalnum())
def model_key(x):return re.sub(r'\s+','',clean(x)).casefold()
# Punctuation/spacing-only variants are grouped automatically. These additional
# groups are explicit manufacturer-name variants. Acquired brands are retained
# separately unless the source itself labels the joint brand (e.g. ADI/MAXIM).
GROUPS={
 'Texas Instruments':['TI','Texas instrument','TI(德州仪器)'],
 'Analog Devices':['Analog Devices Inc.'],
 'Maxim Integrated':['MAXIM','Analog Devices Inc Maxim Integrated','ADI/MAXIM','ADI(亚德诺)/MAXIM(美信)'],
 'Infineon':['Infineon Technologies'],
 'Renesas':['Renesas Electronics','Intersil Renesas Electronics','RENESAS/IDT'],
 'STMicroelectronics':['STMicroelectronics Inc'],
 'Microchip Technology':['Microchip Tech','MICROCHIP'],
 'NXP Semiconductors':['NXP Semicon','NXP USA Inc.'],
 'onsemi':['ON Semiconductor','ON Semicon','ON Semicon ON'],
 'ROHM Semiconductor':['ROHM Semicon'],
 'Vishay Intertechnology':['Vishay Intertech'],
 'Brightking':['Brightking Elec (TAIWAN)'],
 'MDD Microdiode Semiconductor':['MDD(Microdiode Electronics)','MDD'],
 'MCC Micro Commercial Components':['Micro Commercial Components MCC','MCC(Micro Commercial Components)','MCC'],
 'Monolithic Power Systems':['Monolithic Power Systems Inc.','Monolithic Power Systems MPS','MPS'],
 'Broadcom':['AVAGO(Broadcom)','Broadcom AVAGO'],
 'Toshiba':['Toshibia'],
 'Wuxi NCE Power Semiconductor':['NCE'],
 'Foshan Blue Rocket Elec':['BLUE ROCKET'],
 'Goodwork':['GOODWORK(固得沃克)'],
 'WILLSEMI Will Semicon':['WILLSEMI(韦尔)'],
 'Bourns':['Bourns Inc.'],
 'Silergy':['Silergy Corp'],
 'NTE ELECTRONICS INC':['NTE ELECTRONICS, INC.'],
}
ALIASES={maker_key(alias):canonical for canonical,aliases in GROUPS.items() for alias in [canonical,*aliases]}
BAD_MAKERS={maker_key(v) for v in ['Made in China','unknown','generic','-','N/A','none']}
def initial_manufacturer(x):return ALIASES.get(maker_key(x),clean(x))
def reject_reason(r):
 name=clean(r['name']);maker=clean(r['manufacturer'])
 if maker_key(maker) in BAD_MAKERS:return 'manufacturer_not_identified'
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/#,+\-]{2,69}',name):return 'noncompact_or_ambiguous_catalog_name'
 if not re.search('[A-Za-z]',name) or not re.search('[0-9]',name):return 'not_a_specific_model'
 if re.search(r'\b(module|board|evaluation|breakout|arduino)\b',str(r.get('package') or ''),re.I):return 'module_or_board_package_pending_review'
 if maker_key(maker)==maker_key('Arduino'):return 'board_manufacturer_pending_scope_review'
 if maker_key(maker)==maker_key('Mini-Circuits') and r.get('catalog_subcategory')=='RF Mixers':return 'passive_or_hybrid_rf_mixer_pending_review'
 if maker_key(maker) in {maker_key('Omron'),maker_key('Omron Electronics')} and name.upper().startswith('EE-SX'):return 'complete_industrial_optical_sensor'
 if maker_key(initial_manufacturer(maker))==maker_key('Texas Instruments') and (re.match(r'^CC[A-Z0-9]*MOD',name,re.I) or re.match(r'^(TPSM|LMZ|PTH|PT[ABCDN]|PTR|DCP0|DCR0)',name,re.I)):return 'wireless_or_power_module_pending_scope_review'
 if re.match(r'^ESP.*(?:WROOM|WROVER)',name,re.I):return 'wireless_pcb_module'
 if maker_key(maker) in {maker_key('Analog Devices'),maker_key('Analog Devices Inc.')} and re.match(r'^LTM(?:46|47|80)[0-9]',name,re.I):return 'power_converter_module_pending_scope_review'
 if re.fullmatch(r'(?:SOT|SOD|TO|SOP|SSOP|TSSOP|QFN|DFN|DIP|MSOP|LQFP)[-_](?:23|123|323|523|89|92|220|252|263|8|16|32|48|64)',name,re.I):return 'package_name_without_specific_part_pending_review'
 if re.search(r'(^|[-_])(EVAL|EVM|EVB|BOOST|LAUNCH|DISCOVERY|NUCLEO|BOARD|KIT|REF|DEMO|SHIELD)([-_]|$)',name,re.I):return 'development_board_or_tool_name'
 if maker_key(initial_manufacturer(maker))==maker_key('Infineon') and name.upper().startswith('LIGHT-FIBER-'):return 'optical_fiber_accessory_pending_scope_review'
 if maker_key(maker) in {maker_key('Analog Devices'),maker_key('Analog Devices Inc.')} and re.match(r'^[123567]B[0-9]',name,re.I):return 'instrumentation_module_family_pending_scope_review'
 return None
