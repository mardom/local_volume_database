import corner
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import astropy.table as table

from collections import Counter

import numpy.ma as ma
import yaml

from astropy import units as u
import astropy.coordinates as coord

## this makes a->z plus aa -> zz for labeling citations
import string
string.ascii_lowercase
long_list = list(string.ascii_lowercase)
for i in list(string.ascii_lowercase):
    for j in list(string.ascii_lowercase):
        long_list.append(i+j)

path = 'data_input/'

def make_latex_value(value, em, ep, **kwargs):
    ul = kwargs.get('ul', False)
    n = kwargs.get('n', 2)
    str_out = ' '
    if ul!=False:
        str_out = '$<' + "{:0.{prec}f}".format(ul, prec=n) +'$'
    elif ma.is_masked(value)==False:
#         if ma.is_masked(value)==False:
#             return str_out
        str_out = '$'+"{:0.{prec}f}".format(value, prec=n)
        if ma.is_masked(em)==False and ma.is_masked(ep)== False :
            if "{:0.{prec}f}".format(em, prec=n) == "{:0.{prec}f}".format(ep, prec=n):
                str_out+='\\pm'+"{:0.{prec}f}".format(em, prec=n)
            else:
                str_out+='_{-'+"{:0.{prec}f}".format(em,prec=n) + '}^{+' +"{:0.{prec}f}".format(ep,prec=n) +'}'
        str_out+='$'
    return str_out
def add_year(table):
    table['year'] = np.zeros(len(table), dtype=int)
    path = '/Users/apace/Documents/local_volume_database/data_input/'
    for i in range(len(table)):
        k = table['key'][i]
        with open(path+ k +'.yaml', 'r') as stream:
            try:
                stream_yaml = yaml.load(stream, Loader=yaml.Loader)

                if 'discovery_year' in stream_yaml['name_discovery'].keys():
                    table['year'][i] = stream_yaml['name_discovery']['discovery_year']
                else:
                    print(stream_yaml['key'], "missing table")
            except yaml.YAMLError as exc:
                print(exc)
    return table['year']

coord.galactocentric_frame_defaults.set('v4.0')
gc_frame = coord.Galactocentric()

def add_coord(table_input):
    c_table_input = coord.SkyCoord(ra=table_input['ra']*u.deg, dec=table_input['dec']*u.deg,  frame='icrs',)
    table_input['ll'] = c_table_input.galactic.l.value
    table_input['bb'] = c_table_input.galactic.b.value

def create_latex_table_name_discovery(output, input_table, **kwargs):
    classification_column = kwargs.get("classification_column", 'confirmed_dwarf')
    classification_output = kwargs.get("classification_output", 'Dwarf Galaxy')
    with open(output, 'w+') as f:
        for i in range(len(input_table)):
            end_line = '\\\\'
            if i == len(input_table)-1:
                end_line=''
            k = input_table['key'][i]
            out_str = '' + input_table['name'][i] + ' & '
            other_name = []
            ref = []
            with open(path+ k +'.yaml', 'r') as stream:
                try:
                    stream_yaml = yaml.load(stream, Loader=yaml.Loader)
        #             out_str = ''
                    if 'other_name' in stream_yaml['name_discovery'].keys():
                        for other_name_list in range(len(stream_yaml['name_discovery']['other_name'])):
                            other_name.append(stream_yaml['name_discovery']['other_name'][other_name_list])
        #             else:
        #                 print(stream_yaml['key'], "missing table")
                    if 'ref_discovery' in stream_yaml['name_discovery'].keys():
                        for other_name_list in range(len(stream_yaml['name_discovery']['ref_discovery'])):
                            x = stream_yaml['name_discovery']['ref_discovery'][other_name_list]
                            x=x.replace('&', '\string&')
                            ref.append(x)
                except yaml.YAMLError as exc:
                    print(exc)
            c = coord.SkyCoord(ra=input_table['ra'][i]*u.degree, dec=input_table['dec'][i]*u.degree)
            x = c.to_string('hmsdms')
            x1 = c.ra.to_string(unit=u.hourangle, sep=":", precision=1, alwayssign=False, pad=True)
            x2 = c.dec.to_string(sep=":", precision=1, alwayssign=True, pad=True)
            place =0
            if len(other_name)>0:
                out_str += other_name[place] + ' & '
            else:
                out_str +=  ' & '
            out_str += x1 + ' & ' + x2  + ' & '
            if len(ref)>0:
                out_str += "\\citet{" +ref[place] +'}' + ' & '
            else:
                out_str +=  ' & '
            place +=1
        #     print(k,  x1, x2)
    #         print( out_str+ ' \\\\')
            if input_table['confirmed_real'][i]==1:
                out_str +=  '  & '
            else:
                out_str +=  ' Cand. & '

            if input_table[classification_column][i]==1:
                out_str +=  classification_output
            elif input_table[classification_column][i]==0:
                out_str +=  '  '        


            f.write( out_str+ ' \\\\'+'\n')
            while len(other_name)>place or len(ref) > place:
                out_str2 = ' & '
                if len(other_name)>place:
                    out_str2 +=  other_name[place]
                out_str2 += ' &&& '
                if len(ref)>place:
                    out_str2 += "\\citet{" + ref[place]+'}'
                out_str2 += ' \\\\ '
                place+=1
                f.write( out_str2+'\n')

def create_latex_table_structure(output, output_citations, input_table):
    citations = []
    letter = []
    with open(output, 'w+') as f:
        for i in range(len(input_table)):
            letter_to_list = []

            ## this adds combines all the citations per object that this table is using
            cite_temp = []
            if ma.is_masked(input_table['ref_structure'][i])==False:
                cite_temp.append(input_table['ref_structure'][i])
            if ma.is_masked(input_table['ref_distance'][i])==False:
                cite_temp.append(input_table['ref_distance'][i])
            if ma.is_masked(input_table['ref_m_v'][i])==False:
                cite_temp.append(input_table['ref_m_v'][i])

            ## unique entries
            cite_temp2 = np.unique(cite_temp)
#             print(input_table['key'][i], cite_temp2)
            ## this checks if a citation has already been used and pulls it, otherwise it finds the next letter to assign to a citation 
            for tt in cite_temp2:
                if  isinstance(tt,str)==False:
                    continue
#                 if not tt:
#                     continue
#                 if len(tt)<5:
#                     continue
                if tt in  citations:
                    letter_to_list.append(letter[citations.index(tt)])
                else:
                    citations.append(tt)
                    letter_to_list.append(long_list[len(letter)])
                    letter.append(long_list[len(letter)])

            letter_to_list_string = ""
            if len(letter_to_list)>0:
                for kk in letter_to_list:
                    letter_to_list_string+=kk  +','
                letter_to_list_string = letter_to_list_string[:-1]

            x = np.random.normal(input_table['rhalf'][i], (input_table['rhalf_em'][i]+input_table['rhalf_ep'][i])/2., 1000)
            if ma.is_masked(input_table['ellipticity_em'][i])==False and ma.is_masked(input_table['ellipticity'][i])==False:
                y = np.random.normal(input_table['ellipticity'][i], (input_table['ellipticity_em'][i]+input_table['ellipticity_ep'][i])/2., 1000)
            else:
                y = np.zeros(len(x))
            if ma.is_masked(input_table['distance_em'][i])==False and ma.is_masked(input_table['distance_ep'][i])==False:
                z = np.random.normal(input_table['distance'][i], (input_table['distance_em'][i]+input_table['distance_ep'][i])/2., 1000)
            else:
                z = np.full(1000, input_table['distance'][i])
            x2 = x[np.logical_and(y>=0, y<1)]
            y2 = y[np.logical_and(y>=0, y<1)]
            z2 = z[np.logical_and(y>=0, y<1)]
            comb = x2 *np.pi/180./60.*1000.*np.sqrt(1. - y2)* z2
            comb2 = comb[~np.isnan(comb)]
            if len(comb2)==0:
                str_rhalf=''
                if ma.is_masked(input_table['rhalf_em'][i])==True or ma.is_masked(input_table['rhalf_ep'][i])==True and ma.is_masked(input_table['rhalf'][i])==False:
                    rh = input_table['distance'][i]*input_table['rhalf'][i]/180./60.*1000.
                    if ma.is_masked(input_table['ellipticity'][i])==False:
                        rh = rh*np.sqrt(1.-input_table['ellipticity'][i])
                    str_rhalf=make_latex_value(rh, input_table['rhalf_em'][i], input_table['rhalf_em'][i], n=1)  
            else:
                mean = corner.quantile(comb2, [.5, .1587, .8413, 0.0227501, 0.97725])
                str_rhalf = make_latex_value(mean[0], mean[0]-mean[1], mean[2]-mean[0], n=1)
        #     rhalf_pc = mean[0]
        #     rhalf_pc_error = (mean[2]-mean[1])/2.

            ## output each row of our table, plus the citations at the end of the line
            f.write(input_table['name'][i] + '&'+"{:0.4f}".format(input_table['ra'][i])+'&'+"{:0.4f}".format(input_table['dec'][i])+'&'+
                  make_latex_value(input_table['rhalf'][i], input_table['rhalf_em'][i], input_table['rhalf_ep'][i], n=2)+'&'+
                 make_latex_value(input_table['ellipticity'][i], input_table['ellipticity_em'][i], input_table['ellipticity_ep'][i], ul=input_table['ellipticity_ul'][i], n=2)+ '& '+
                  make_latex_value(input_table['position_angle'][i], input_table['position_angle_em'][i], input_table['position_angle_ep'][i], n=1)+ '& '+
                  str_rhalf + '& '+
                  make_latex_value(input_table['distance_modulus'][i], input_table['distance_modulus_em'][i], input_table['distance_modulus_ep'][i], n=2)+' & '+
                 make_latex_value(input_table['distance'][i], input_table['distance_em'][i], input_table['distance_ep'][i], n=1)+ ' & '+ make_latex_value(input_table['apparent_magnitude_v'][i], np.ma.masked, np.ma.masked, n=1)+ ' & '+
                   make_latex_value(input_table['M_V'][i], input_table['M_V_em'][i], input_table['M_V_ep'][i], n=1)+ ' & '+ letter_to_list_string+
                  '\\\\'+'\n')
    with open(output_citations, 'w+') as f:
        for i,j in zip(letter, citations):
        #     print(i, j)
            j = j.replace('&', '\string&')
            f.write( "("+i+") \citet{"+j+"}\n",)

def create_latex_table_kinematics(output, output_citations, input_table):
    citations = []
    letter = []
    with open(output, 'w+') as f:
        for i in range(len(input_table)):
    #         print(input_table['key'][i])
            letter_to_list = []

            ## this adds combines all the citations per object that this table is using
            cite_temp = []
            if ma.is_masked(input_table['ref_vlos'][i])==False:
                cite_temp.append(input_table['ref_vlos'][i])
            if ma.is_masked(input_table['ref_proper_motion'][i])==False:
                cite_temp.append(input_table['ref_proper_motion'][i])

            ## unique entries
    #         if not cite_temp:
    # #             print(input_table['key'][i])
    #             f.write(input_table['name'][i]+
    #               '\\\\'+'\n')
    #             continue

            cite_temp2 = np.unique(cite_temp)
    #         print(cite_temp, cite_temp2)
            ## this checks if a citation has already been used and pulls it, otherwise it finds the next letter to assign to a citation 
    #         if not cite_temp:
            for tt in cite_temp2:
                if  isinstance(tt,str)==False:
                    continue
                if tt in  citations:
                    letter_to_list.append(letter[citations.index(tt)])
                else:
                    citations.append(tt)
                    letter_to_list.append(long_list[len(letter)])
                    letter.append(long_list[len(letter)])

            letter_to_list_string = ""
            if len(letter_to_list)>0:
                for kk in letter_to_list:
                    letter_to_list_string+=kk  +','
                letter_to_list_string = letter_to_list_string[:-1]

            f.write(input_table['name'][i]+ '&'+"{:0.4f}".format(input_table['ll'][i])+'&'+"{:0.4f}".format(input_table['bb'][i])+'&'+ make_latex_value(input_table['vlos_systemic'][i], input_table['vlos_systemic_em'][i], input_table['vlos_systemic_ep'][i], n=1)+ '& '+
               make_latex_value(input_table['vlos_sigma'][i], input_table['vlos_sigma_em'][i], input_table['vlos_sigma_ep'][i], ul=input_table['vlos_sigma_ul'][i], n=2)+ '& '+
                    make_latex_value(input_table['metallicity_spectroscopic'][i], input_table['metallicity_spectroscopic_em'][i], input_table['metallicity_spectroscopic_ep'][i], n=2)+'&'+
                 make_latex_value(input_table['metallicity_spectroscopic_sigma'][i], input_table['metallicity_spectroscopic_sigma_em'][i], input_table['metallicity_spectroscopic_sigma_ep'][i], ul=input_table['metallicity_spectroscopic_sigma_ul'][i],  n=2)+ '& '+
                  make_latex_value(input_table['pmra'][i], input_table['pmra_em'][i], input_table['pmra_ep'][i], n=3)+'&'+
                 make_latex_value(input_table['pmdec'][i], input_table['pmdec_em'][i], input_table['pmdec_ep'][i],  n=3)+ '& '+
                  letter_to_list_string+
                  '\\\\'+'\n')
    with open(output_citations, 'w+') as f:
        for i,j in zip(letter, citations):
        #     print(i, j)
            j = j.replace('&', '\string&')
            f.write( "("+i+") \citet{"+j+"}\n",)


dsph_mw = table.Table.read('data/dwarf_mw.csv')
dsph_m31 = table.Table.read('data/dwarf_m31.csv')
dsph_lf = table.Table.read('data/dwarf_local_field.csv')
gc_ufsc = table.Table.read('data/gc_ufsc.csv')
gc_disk = table.Table.read('data/gc_disk.csv')
gc_harris = table.Table.read('data/gc_harris.csv')
gc_dwarf = table.Table.read('data/gc_dwarf_hosted.csv')

dsph_mw['year'] = add_year(dsph_mw)
dsph_m31['year'] = add_year(dsph_m31)
dsph_lf['year'] = add_year(dsph_lf)

gc_ufsc['year'] = add_year(gc_ufsc)
gc_disk['year'] = add_year(gc_disk)
gc_harris['year'] = add_year(gc_harris)
gc_dwarf['year'] = add_year(gc_dwarf)

add_coord(dsph_m31)
add_coord(dsph_mw)
add_coord(dsph_lf)

add_coord(gc_ufsc)
add_coord(gc_harris)
add_coord(gc_disk)

add_coord(gc_dwarf)

dsph_mw.sort(['year', 'name'])
create_latex_table_name_discovery('table/table_data/dwarf_mw_name_discovery_data.tex', dsph_mw)
dsph_mw2 = dsph_mw[dsph_mw['key']!='LMC']
dsph_mw2 = dsph_mw2[dsph_mw2['key']!='SMC']
dsph_mw2.sort('name')
create_latex_table_structure('table/table_data/dwarf_mw_structure_data.tex', 'table/table_data/dwarf_mw_structure_citations.tex', dsph_mw2)
create_latex_table_kinematics('table/table_data/dwarf_mw_kinematics_data.tex', 'table/table_data/dwarf_mw_kinematics_citations.tex', dsph_mw2)

dsph_m31.sort(['year', 'name'])
create_latex_table_name_discovery('table/table_data/dwarf_m31_name_discovery_data.tex', dsph_m31)
dsph_m31.sort('name')
create_latex_table_structure('table/table_data/dwarf_m31_structure_data.tex', 'table/table_data/dwarf_m31_structure_citations.tex', dsph_m31)
create_latex_table_kinematics('table/table_data/dwarf_m31_kinematics_data.tex', 'table/table_data/dwarf_m31_kinematics_citations.tex', dsph_m31)

dsph_lf.sort(['year', 'name'])
create_latex_table_name_discovery('table/table_data/dwarf_lf_name_discovery_data.tex', dsph_lf)
dsph_lf.sort('name')
create_latex_table_structure('table/table_data/dwarf_lf_structure_data.tex', 'table/table_data/dwarf_lf_structure_citations.tex', dsph_lf)
create_latex_table_kinematics('table/table_data/dwarf_lf_kinematics_data.tex', 'table/table_data/dwarf_lf_kinematics_citations.tex', dsph_lf)

gc_ufsc.sort(['year', 'name'])
create_latex_table_name_discovery('table/table_data/gc_ufsc_name_discovery_data.tex', gc_ufsc, classification_column='confirmed_star_cluster', classification_output='Star Cluster')
gc_ufsc.sort('name')
create_latex_table_structure('table/table_data/gc_ufsc_structure_data.tex', 'table/table_data/gc_ufsc_structure_citations.tex', gc_ufsc)
create_latex_table_kinematics('table/table_data/gc_ufsc_kinematics_data.tex', 'table/table_data/gc_ufsc_kinematics_citations.tex', gc_ufsc)

gc_disk.sort(['year', 'name'])
create_latex_table_name_discovery('table/table_data/gc_disk_name_discovery_data.tex', gc_disk, classification_column='confirmed_star_cluster', classification_output='Star Cluster')
gc_disk.sort('name')
create_latex_table_structure('table/table_data/gc_disk_structure_data.tex', 'table/table_data/gc_disk_structure_citations.tex', gc_disk)
create_latex_table_kinematics('table/table_data/gc_disk_kinematics_data.tex', 'table/table_data/gc_disk_kinematics_citations.tex', gc_disk)

gc_harris.sort(['year', 'name'])
create_latex_table_name_discovery('table/table_data/gc_harris_name_discovery_data.tex', gc_harris, classification_column='confirmed_star_cluster', classification_output='Star Cluster')
gc_harris.sort('name')
create_latex_table_structure('table/table_data/gc_harris_structure_data.tex', 'table/table_data/gc_harris_structure_citations.tex', gc_harris)
create_latex_table_kinematics('table/table_data/gc_harris_kinematics_data.tex', 'table/table_data/gc_harris_kinematics_citations.tex', gc_harris)

gc_dwarf.sort(['year', 'name'])
create_latex_table_name_discovery('table/table_data/gc_dwarf_name_discovery_data.tex', gc_dwarf, classification_column='confirmed_star_cluster', classification_output='Star Cluster')
gc_dwarf.sort('name')
create_latex_table_structure('table/table_data/gc_dwarf_structure_data.tex', 'table/table_data/gc_dwarf_structure_citations.tex', gc_dwarf)
create_latex_table_kinematics('table/table_data/gc_dwarf_kinematics_data.tex', 'table/table_data/gc_dwarf_kinematics_citations.tex', gc_dwarf)