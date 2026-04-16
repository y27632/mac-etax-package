import json
import os
import re
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

# Matches JNENGAPPI date strings like "5,08,03,31" (era,yy,mm,dd)
_JNENGAPPI_RE = re.compile(r'^(\d),(\d{2}),(\d{2}),(\d{2})$')

# Namespace constants
N_HOJIN = "http://xml.e-tax.nta.go.jp/XSD/hojin"
N_GEN = "http://xml.e-tax.nta.go.jp/XSD/general"
N_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
N_DSIG = "http://www.w3.org/2000/09/xmldsig#"

class ETaxDocument:
    def __init__(self, procedure_cd, proc_vr, it_info):
        self.procedure_cd = procedure_cd
        self.proc_vr = proc_vr
        self.it_info = it_info
        self.forms = [] 
    
    def add_form(self, form_id, vr, contents_dict):
        self.forms.append({
            'id': form_id,
            'vr': vr,
            'data': contents_dict
        })

    def _dict_to_xml_wrapper(self, form_id, vr, d):
        indent = "      "
        xml = []
        xml.append(f'{indent}<{form_id} id="{form_id}" VR="{vr}" softNM="EveryScience-xtx-v2" sakuseiNM="EveryScience-xtx-v2" sakuseiDay="{datetime.now().strftime("%Y-%m-%d")}">')
        for k, v in d.items():
            if v is not None:
                xml.append(self._dict_to_xml_real(k, v, indent + "  "))
        xml.append(f"{indent}</{form_id}>")
        return "\n".join(xml)

    def _dict_to_xml_real(self, tag_name, d, indent):
        xml = []
        if isinstance(d, dict):
            if not d:
                # Use standard self-closing for empty containers
                xml.append(f"{indent}<{tag_name}/>")
            else:
                xml.append(f"{indent}<{tag_name}>")
                for k, v in d.items():
                    if v is not None:
                         xml.append(self._dict_to_xml_real(k, v, indent + "  "))
                xml.append(f"{indent}</{tag_name}>")
        elif isinstance(d, list):
             for el in d:
                 if el is not None:
                     xml.append(self._dict_to_xml_real(tag_name, el, indent))
        else:
            if isinstance(d, str) and d.startswith("REF:"):
                ref_target = d.split(":")[1]
                xml.append(f'{indent}<{tag_name} IDREF="{ref_target}"/>')
            elif hasattr(d, '__str__') and str(d).startswith("REF:"):
                xml.append(f'{indent}<{tag_name} IDREF="{str(d).split(":")[1]}"/>')
            elif d == "":
                xml.append(f"{indent}<{tag_name}/>")
            else:
                m = _JNENGAPPI_RE.match(str(d))
                if m:
                    era, yy, mm, dd = m.groups()
                    inner = f'<gen:era>{era}</gen:era><gen:yy>{yy}</gen:yy><gen:mm>{mm}</gen:mm><gen:dd>{dd}</gen:dd>'
                    xml.append(f"{indent}<{tag_name}>{inner}</{tag_name}>")
                else:
                    xml.append(f"{indent}<{tag_name}>{xml_escape(str(d))}</{tag_name}>")
        return "\n".join(xml)

    def _build_it_header(self):
        it_xml = []
        it_xml.append('      <IT id="IT" VR="1.5">')
        def add(tag, xmlstring):
            if xmlstring:
                it_xml.append(f'        <{tag} ID="{tag}">{xmlstring}</{tag}>')
        info = self.it_info
        # Strict order & Fixed tags
        zeimusho_inner = f'<gen:zeimusho_CD>{xml_escape(str(info.get("zeimusho_cd", "")))}</gen:zeimusho_CD>'
        if info.get("zeimusho_nm"):
            zeimusho_inner += f'<gen:zeimusho_NM>{xml_escape(info["zeimusho_nm"])}</gen:zeimusho_NM>'
        add('ZEIMUSHO', zeimusho_inner)
        if info.get("teisyutsu_day"):
            y, yy, mm, dd = info["teisyutsu_day"].split(',')
            add('TEISYUTSU_DAY', f'<gen:era>{y}</gen:era><gen:yy>{yy}</gen:yy><gen:mm>{mm}</gen:mm><gen:dd>{dd}</gen:dd>')
        add('NOZEISHA_ID', info.get("nozeisha_id"))
        if info.get("nozeisha_bango"):
            add('NOZEISHA_BANGO', f'<gen:hojinbango>{xml_escape(info["nozeisha_bango"])}</gen:hojinbango>')
        if info.get("nozeisha_nm_kn"):
            add('NOZEISHA_NM_KN', xml_escape(info["nozeisha_nm_kn"]))
        if info.get("nozeisha_nm"):
            add('NOZEISHA_NM', xml_escape(info["nozeisha_nm"]))
        if info.get("nozeisha_adr"):
            add('NOZEISHA_ADR', xml_escape(info["nozeisha_adr"]))
        if info.get("nozeisha_tel"):
            t1, t2, t3 = info["nozeisha_tel"].split('-')
            add('NOZEISHA_TEL', f'<gen:tel1>{t1}</gen:tel1><gen:tel2>{t2}</gen:tel2><gen:tel3>{t3}</gen:tel3>')
        if info.get("shihon_kin") is not None:
            add('SHIHON_KIN', str(info["shihon_kin"]))
        if info.get("jigyo_naiyo"):
            add('JIGYO_NAIYO', xml_escape(info["jigyo_naiyo"]))
        if info.get("daihyo_nm_kn"):
            add('DAIHYO_NM_KN', xml_escape(info["daihyo_nm_kn"]))
        if info.get("daihyo_nm"):
            add('DAIHYO_NM', xml_escape(info["daihyo_nm"]))
        if info.get("daihyo_adr"):
            add('DAIHYO_ADR', xml_escape(info["daihyo_adr"]))
        add('TETSUZUKI', f'<procedure_CD>{self.procedure_cd}</procedure_CD>')
        if info.get("nendo_from"):
            y, yy, mm, dd = info["nendo_from"].split(',')
            add('JIGYO_NENDO_FROM', f'<gen:era>{y}</gen:era><gen:yy>{yy}</gen:yy><gen:mm>{mm}</gen:mm><gen:dd>{dd}</gen:dd>')
        if info.get("nendo_to"):
            y, yy, mm, dd = info["nendo_to"].split(',')
            add('JIGYO_NENDO_TO', f'<gen:era>{y}</gen:era><gen:yy>{yy}</gen:yy><gen:mm>{mm}</gen:mm><gen:dd>{dd}</gen:dd>')
        it_xml.append('      </IT>')
        return "\n".join(it_xml)

    def generate(self, output_path):
        xml = [
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            f'<DATA xmlns="{N_HOJIN}" xmlns:gen="{N_GEN}" xmlns:rdf="{N_RDF}" xmlns:dsig="{N_DSIG}">',
            f'  <{self.procedure_cd} id="{self.procedure_cd}" VR="{self.proc_vr}">',
            '    <CATALOG id="CATALOG">',
            '      <rdf:RDF>',
            '        <rdf:Description id="REPORT">',
            '          <SEND_DATA/>',
            '          <IT_SEC>',
            '            <rdf:Description about="#IT"/>',
            '          </IT_SEC>',
            '          <FORM_SEC>',
            '            <rdf:Seq>'
        ]
        for f in self.forms:
            xml.append(f'              <rdf:li><rdf:Description about="#{f["id"]}"/></rdf:li>')
        xml.extend([
            '            </rdf:Seq>',
            '          </FORM_SEC>',
            '          <TENPU_SEC/>',
            '          <XBRL_SEC/>',
            '          <XBRL2_1_SEC/>',
            '          <SOFUSHO_SEC/>',
            '          <ATTACH_SEC/>',
            '          <CSV_SEC/>',
            '        </rdf:Description>',
            '      </rdf:RDF>',
            '    </CATALOG>',
            '    <CONTENTS id="CONTENTS">'
        ])
        xml.append(self._build_it_header())
        for f in self.forms:
            xml.append(self._dict_to_xml_wrapper(f['id'], f['vr'], f['data']))
        xml.extend([
            '    </CONTENTS>',
            f'  </{self.procedure_cd}>',
            '</DATA>'
        ])
        final_xml = "\n".join(xml)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(final_xml)
