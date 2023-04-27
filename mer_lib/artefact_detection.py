import math

import numpy as np
import statistics

import scipy.signal as sig
import scipy.io as io
import statsmodels.tsa.stattools as st_tools

def max_diff_psd(data):


    psd_thr = 0.01

    dat  = data.data()
    freqs = data.get_freqs()

    res_data = []
    for i in range(len(dat)):
        seconds = math.ceil(dat[i].shape/freqs[i])
        fs = freqs[i]
        data_sub = []
        for secs in range(seconds):
            s_e = [int(secs*fs), min(int((secs+1)*fs),int(dat[i].shape[0]))]  #start end
            feat = _compute_features(dat[i],s_e,fs) #compute psd
            data_sub.append(feat)
        res_data.append(data_sub)

    #data.set_data(np.array(res_data))

    data.mask_label_threshold = np.array(res_data) < psd_thr
    return data


def covariance_method(data):
    """Covariance Method For artefact detection"""
    threshold = 1.2

    da = data.data

    fs = data.get_freqs()

    [times,_] = data.get_anat_landmarks()
    ###create subdivisions in dataset
    ###
    ###
    subdivisions = []

    for i in range(len(times)):
        if i+1 < len(times):
            for e_ind in range(da.shape[0]):
                freq = fs[e_ind]
                if len(subdivisions) < e_ind+1:
                    subdivisions.append([])
                subdivisions[e_ind].append(da[e_ind,int(freq*times[i]):int(freq*times[i+1])])
        else:
            for e_ind in range(da.shape[0]):
                freq = fs[e_ind]
                if len(subdivisions) < e_ind:
                    subdivisions.append([])
                subdivisions[e_ind].append(da[e_ind,int(freq*times[i]):])


    for i in range(da.shape[0]):
        for j in range(len(times)):
            subdivisions[i][j] = subdivisions[i][j] - np.nanmean(subdivisions[i][j])

    resarr = []
    for i in range(da.shape[0]):
        tmp = []
        for j in range(len(times)):
            res = _compute_cov(subdivisions[i][j],threshold,fs[i]/3)
            tmp.append(res)
        resarr.append(tmp)
    resarr = np.array(resarr)
    resarr = resarr.reshape((resarr.shape[0],resarr.shape[1]*resarr.shape[2]))

    indmax = da.shape[0]
    da = []

    for i in range(indmax):
        tmp = None
        for j in range(len(times)):
            if tmp is None:
                tmp = subdivisions[i][j]
            else:
                tmp = np.concatenate((tmp,subdivisions[i][j]))
        da.append(tmp)
    da = np.array(da)
    da[resarr==0] = np.NAN

    res_markings = []
    # for i in range(da.shape[0]):
    #     seconds = math.ceil(da[i].shape/fs[i])
    #     fse = fs[i]
    #     data_sub = []
    #     for secs in range(seconds):
    #         s_e = [int(secs*fse), min(int((secs+1)*fse),int(da[i].shape[0]))]  #start end
    #         if not resarr[i, s_e[0]:s_e[1]].min():
    #             data_sub.append(0)
    #         else:
    #             data_sub.append(1)
    #     res_markings.append(data_sub)

    data.set_data(da)
    data.mask_label_threshold = np.array(resarr)
    return data




    pass


def _compute_cov(signal, threshold, segm_len):
    """

    :param signal:
    :param threshold:
    :param segm_len:
    :return:
    """
    #normalise
    signal_t= (signal- np.nanmean(signal))/np.nanstd(signal)



    seconds = math.ceil(signal_t.shape[0] / segm_len)

    indices = []
    data_sub = []
    for secs in range(seconds):
        s_e = [int(secs * segm_len), min(int((secs + 1) * segm_len), int(signal_t.shape[0]))]  # start end
        indices.append(s_e)
        data_sub.append(signal_t[s_e[0]:s_e[1]])
    res_data = data_sub

    covs = []
    for col in range(len(res_data)):

        tmp = st_tools.acovf(res_data[col])
        #tmp = tmp[round(tmp.shape[0]/2):tmp.shape[0]]
        covs.append(tmp)
    covs = np.array(covs).transpose()
    variances= np.var(covs,axis=0)

    dists_raw = np.zeros((variances.shape[0],variances.shape[0]))
    for i in range(len(variances)):
        for j in range(i,len(variances)):
            if i == j:
                #distances[i,j] = 0
                dists_raw[i,j] = 0
            else:
                tmp = max([variances[i],variances[j]])/min([variances[i],variances[j]])
                dists_raw[i,j ] = tmp
                dists_raw[j, i] = tmp
                # if tmp > threshold:
                #     distances[i, j] = 0
                #     distances[j, i] = 0
                # else:
                #     distances[i, j] = 1
                #     distances[j, i] = 1

    dist_mask = dists_raw < threshold
    #
    # Longest segment
    #
    comp = np.zeros((dist_mask.shape[0]))
    actual_component = 0
    while (0 in comp):

        op = [np.where(comp == 0)[0][0]]
        actual_component = actual_component +1
        closed = []
        while (len(op) > 0):
            comp[op[0]] = actual_component

            #adjastent elements derived from row or collumn
            adj_to_op = dist_mask[op[0],:]

            children = np.where(adj_to_op == 1)[0]
            for i in range(children.shape[0]):
                if not (( children[i] in op ) or (children[i] in closed)):
                    op.append(children[i])

            closed.append(op[0])
            op.pop(0)
        pass
    pass

    comp_len = np.zeros((comp.shape[0]))
    for cur in range(comp_len.shape[0]):
        comp_len[cur] = sum(comp==cur)
    ind_max = np.where(comp_len == max(comp_len))[0][0]

    resarr = np.zeros((signal.shape[0]))
    for i in range(len(indices)):
        if comp[i] == ind_max:
            resarr[indices[i][0]:indices[i][1]] = 1
    return resarr









def _compute_features(signal,start_end,freq):

    feat_vals = []

    segment = signal[start_end[0]:start_end[1]]
    l_seg = segment.shape[0]
    is_nan = np.isnan(segment)


    if ~(is_nan.sum() < l_seg):
        print("warning")
        pass
    NFFT = 2048 #fft len
    seg_norm = segment / ( np.sqrt(np.nanmean(np.power(segment,2))) )

    # mean clean PSD spectrum - calculated on clean segments of 60 train
    meanClnPSD = [4.77562431760460e-05, 0.000166178838654735, 0.000227806114901376, 0.000146040306929677,
                  0.000142911335033798, 0.000192389466398494, 0.000241298241799244, 0.000313328240515836,
                  0.000551530514429587, 0.000676116046498073, 0.000589870009775301, 0.000666057276492933,
                  0.000976870506074863, 0.00153008829774771, 0.00111734213373207, 0.00118978582786262,
                  0.00138826592498130, 0.00183274813159608, 0.00166025979142410, 0.00172365391321772,
                  0.00187407420905555, 0.00232046231406939, 0.00231718653722749, 0.00223308922838443,
                  0.00229458106215795, 0.00249993684340288, 0.00265075493463280, 0.00270928586528559,
                  0.00290230525509276, 0.00311006754409378, 0.00343268066344955, 0.00329037019721431,
                  0.00334454943324877, 0.00344422750530643, 0.00341031274248160, 0.00341195297684773,
                  0.00349486459313133, 0.00359357475245854, 0.00396922454483106, 0.00406929313602893,
                  0.00411443190955744, 0.00417929900513955, 0.00399602431438698, 0.00411053910110060,
                  0.00413623833438308, 0.00422796555655805, 0.00442006297486236, 0.00450079497340097,
                  0.00449572150989367, 0.00459150757377476, 0.00480359422910404, 0.00477445815618844,
                  0.00467302146324857, 0.00475741028179341, 0.00466343919152143, 0.00479140294729342,
                  0.00490962350523759, 0.00495305358928402, 0.00492313075478619, 0.00494184122580270,
                  0.00507271776515933, 0.00497804382483539, 0.00491620260712145, 0.00497576630307890,
                  0.00504328104327651, 0.00500239299106261, 0.00505212342917972, 0.00500623040375661,
                  0.00511808393864830, 0.00517149453283253, 0.00515532861107924, 0.00525727966706852,
                  0.00532564371679703, 0.00524950588753595, 0.00513195437617655, 0.00515258273909534,
                  0.00525297852364360, 0.00518068254349220, 0.00516886501298688, 0.00525421453752356,
                  0.00521933405230834, 0.00522291129028569, 0.00515097660980339, 0.00513469256030222,
                  0.00509685952940660, 0.00513033954767364, 0.00510540184120212, 0.00511239023673139,
                  0.00510007133642861, 0.00515262337645407, 0.00509412434890254, 0.00499609041421214,
                  0.00498431690873961, 0.00499109119680796, 0.00500562129446170, 0.00495958712223161,
                  0.00502210600501136, 0.00508880992250116, 0.00517377931021268, 0.00505011303168902,
                  0.00505528149348956, 0.00500098263183940, 0.00499810504945096, 0.00492261532910077,
                  0.00496610863134506, 0.00497472013897678, 0.00490580239360861, 0.00482089626038923,
                  0.00475508596774923, 0.00474499271537251, 0.00477645929755003, 0.00475545145715365,
                  0.00478105644166975, 0.00465488152469854, 0.00471409717536129, 0.00471048021369165,
                  0.00475915457598463, 0.00468940956222786, 0.00462034906737799, 0.00449382096630521,
                  0.00451091562820079, 0.00454705830525373, 0.00455982028848946, 0.00446689456067388,
                  0.00445675377991204, 0.00444786821089221, 0.00439386079321514, 0.00447871981464816,
                  0.00442405879331474, 0.00439621058676603, 0.00437314571485769, 0.00423853279637452,
                  0.00432281038873557, 0.00428664394427408, 0.00420520265904031, 0.00420277442594741,
                  0.00419779497156240, 0.00416879314864072, 0.00410729046859493, 0.00400428675858715,
                  0.00405876046320252, 0.00410178417379235, 0.00397467089452320, 0.00391046801293594,
                  0.00391752187150546, 0.00388483532227158, 0.00386087601599158, 0.00385741600500733,
                  0.00382291959822417, 0.00383491328601276, 0.00376932951838254, 0.00368331069678440,
                  0.00371123558130991, 0.00366310738526172, 0.00364366432217688, 0.00362413382217811,
                  0.00354570588820700, 0.00358475706353929, 0.00366862215868109, 0.00351006826610550,
                  0.00345978657800265, 0.00342900994917641, 0.00339385866148339, 0.00336125790170430,
                  0.00339453771900013, 0.00331911911350546, 0.00329870399182654, 0.00328714338438837,
                  0.00328874618744437, 0.00327686272574081, 0.00324735483354771, 0.00322155179713891,
                  0.00315570229917142, 0.00315326110916976, 0.00319684641646357, 0.00314736171834294,
                  0.00306681677500525, 0.00301049225149239, 0.00300742249482694, 0.00302020068853759,
                  0.00298394947205322, 0.00295828496246546, 0.00295793639653616, 0.00294729960938506,
                  0.00288618218091725, 0.00287939586512066, 0.00288281375613166, 0.00286836338449627,
                  0.00285755463853944, 0.00279416086371548, 0.00270718061793415, 0.00271371249989810,
                  0.00270919503275142, 0.00269729330913122, 0.00269408511581507, 0.00267720221524766,
                  0.00264801544357892, 0.00263377346083732, 0.00262111731761184, 0.00263595262004538,
                  0.00262626968521818, 0.00261661460063328, 0.00250243478137951, 0.00248250812259610,
                  0.00245990029590071, 0.00245886232108565, 0.00246224867222939, 0.00242636884710659,
                  0.00239949345834174, 0.00237552764431891, 0.00239456292005979, 0.00235664221929828,
                  0.00230486147795030, 0.00247973206258655, 0.00268951184804001, 0.00228710246732938,
                  0.00220864511020846, 0.00218157917992252, 0.00218259776769702, 0.00214869175208088,
                  0.00212158964037666, 0.00208024229172271, 0.00212793967087608, 0.00206507769806619,
                  0.00207025116067468, 0.00203882462468301, 0.00203359939070705, 0.00202612148388391,
                  0.00204754318184759, 0.00196389620383922, 0.00195354774577354, 0.00197032387955965,
                  0.00195452996560773, 0.00192208273341569, 0.00191009257630677, 0.00191076341976409,
                  0.00187829312137760, 0.00182625944094375, 0.00179086603108449, 0.00179871090759119,
                  0.00177741456196684, 0.00176465492671573, 0.00174715201493156, 0.00177208801878110,
                  0.00175460360420476, 0.00171475916784424, 0.00171461191245323, 0.00171989254168275,
                  0.00169053441597643, 0.00165043547530270, 0.00168051444830999, 0.00166285226395527,
                  0.00162966127418428, 0.00162595616198859, 0.00163267839345235, 0.00159762766965056,
                  0.00161062958055545, 0.00157638671573888, 0.00154936250712022, 0.00153402998560929,
                  0.00156841336528123, 0.00154897631742393, 0.00148062230251802, 0.00151891986972174,
                  0.00151300911069890, 0.00148996111047519, 0.00147552541465048, 0.00145337081960274,
                  0.00147913373957561, 0.00152326697458419, 0.00144671943556326, 0.00139510403541311,
                  0.00136375026650744, 0.00136915971522884, 0.00136445738926030, 0.00135653074777702,
                  0.00135125142196236, 0.00137363677471252, 0.00135755037872982, 0.00129294316898353,
                  0.00129724586299263, 0.00128041227861883, 0.00129219670710612, 0.00127100355594330,
                  0.00124674711239799, 0.00123654274371625, 0.00123468554428219, 0.00121521862163789,
                  0.00119839984048907, 0.00118088546307052, 0.00119330814308405, 0.00117635913832556,
                  0.00114275440482225, 0.00113522811181218, 0.00114878803924825, 0.00115640819464204,
                  0.00113779751342715, 0.00112207344399758, 0.00110816205369944, 0.00109700301580710,
                  0.00109091009632187, 0.00108894759507681, 0.00107272826146688, 0.00110889342564740,
                  0.00106181762777779, 0.00103718414969366, 0.00103782216972429, 0.00101438481238316,
                  0.000999398724652642, 0.00100855972082798, 0.000992670464595343, 0.000993106274414697,
                  0.000987135064253253, 0.000966204342528641, 0.000971652513735865, 0.000968032044291694,
                  0.000958601124217830, 0.000951318696509442, 0.000945095679679914, 0.000946593729861222,
                  0.000925784758955504, 0.000886789004767534, 0.000902230823285457, 0.000882729607039601,
                  0.000880630403924362, 0.000867110609988293, 0.000872032444304620, 0.000870070347674444,
                  0.000877204091176647, 0.000865341380362729, 0.000847223092148180, 0.000835187040099669,
                  0.000839695954697677, 0.000845348070450712, 0.000823489555381757, 0.000831918270618146,
                  0.000805011115725262, 0.000803496327487231, 0.000784889528471347, 0.000772008578721483,
                  0.000770513995547345, 0.000750230422750691, 0.000742106641658372, 0.000752693293885436,
                  0.000733240046195243, 0.000713192459157332, 0.000723622827320018, 0.000723554305401711,
                  0.000711056990146928, 0.000697823180835042, 0.000686916484669332, 0.000687069406791615,
                  0.000688355141769348, 0.000683167806269009, 0.000656005693033487, 0.000644314773263546,
                  0.000638489836566494, 0.000651305582588892, 0.000646758030301500, 0.000640562414538154,
                  0.000622987735346499, 0.000610607783523218, 0.000618507347065954, 0.000619508065463372,
                  0.000606345491819543, 0.000603250619787423, 0.000592051355089845, 0.000571299147710659,
                  0.000564521927073995, 0.000562252070357333, 0.000548058553576822, 0.000567593554269263,
                  0.000559049591044400, 0.000546368184672955, 0.000534202832480463, 0.000521001303156587,
                  0.000509118486151177, 0.000503513649718214, 0.000498335208055070, 0.000489919143470776,
                  0.000489839565999609, 0.000482608022147641, 0.000474500695441070, 0.000456016012191429,
                  0.000452992804030727, 0.000447008353698699, 0.000442436060154468, 0.000429780785250373,
                  0.000415298807303484, 0.000413535174192959, 0.000405719045548631, 0.000391300610860691,
                  0.000380704557441276, 0.000376823742965357, 0.000366443461994963, 0.000360427105607389,
                  0.000356257553553216, 0.000343963017867418, 0.000339594141435343, 0.000327416262669204,
                  0.000311785071102165, 0.000296233652795617, 0.000289778595145242, 0.000280723531277823,
                  0.000270074021530794, 0.000263095315827241, 0.000252779736596250, 0.000243343133141444,
                  0.000233664551961454, 0.000222888038805312, 0.000215788801633336, 0.000205419463213638,
                  0.000195807888998832, 0.000187787179005757, 0.000180919580096046, 0.000170097584386522,
                  0.000158303917583322, 0.000149189914694997, 0.000142768041927102, 0.000135775822618333,
                  0.000128520745336136, 0.000116678582371879, 0.000109189924972610, 0.000102296436265799,
                  9.70852943037977e-05, 8.99677696901637e-05, 8.37943404557717e-05, 7.84590810288204e-05,
                  6.98675682491148e-05, 6.37113507154509e-05, 6.02438323624790e-05, 5.41515998931824e-05,
                  4.94706771062464e-05, 4.59255080687316e-05, 4.11370318253974e-05, 3.72350614959839e-05,
                  3.26683097946813e-05, 2.92831773481897e-05, 2.57157730167172e-05, 2.34101274978662e-05,
                  2.13581789005654e-05, 1.85068535340041e-05, 1.62579772348467e-05, 1.41084871984134e-05,
                  1.24022267251321e-05, 1.09745684720539e-05, 9.49371390203570e-06, 8.13492590269067e-06,
                  6.92512690619028e-06, 5.89814033220041e-06, 4.95101609390562e-06, 4.10480825875449e-06,
                  3.43481776593233e-06, 2.88106330105423e-06, 2.35491029065358e-06, 1.91646119690768e-06,
                  1.53589565395398e-06, 1.25092631588289e-06, 1.00505342772475e-06, 8.03861393774004e-07,
                  6.64701374447933e-07, 5.48189579375301e-07, 4.55966023111770e-07, 3.90410096705582e-07,
                  3.53826424888033e-07, 3.41742399633712e-07, 3.45212243845645e-07, 3.45394260859671e-07,
                  3.51233748378259e-07, 3.71856158341656e-07, 3.86058023920602e-07, 4.13228272070997e-07,
                  4.34293625655231e-07, 4.82681055375979e-07, 5.14072929203551e-07, 5.26494309026015e-07,
                  5.33654909090267e-07, 5.58642050558073e-07, 5.70769509206151e-07, 5.72148112840766e-07,
                  5.92208682381448e-07, 6.00174293994549e-07, 6.04443036260513e-07, 6.03471315488289e-07,
                  5.98817274790035e-07, 5.93448636484945e-07, 5.74484831076828e-07, 5.67372196217104e-07,
                  5.64618694395925e-07, 5.49553802910645e-07, 5.36937738816994e-07, 5.24375371781841e-07,
                  5.11454367770285e-07, 4.77871921869496e-07, 4.61715561992907e-07, 4.56400082911407e-07,
                  4.49690180876640e-07, 4.30204413224156e-07, 4.06516943215753e-07, 3.86949554790614e-07,
                  3.75085286153522e-07, 3.60583674200204e-07, 3.41043116702204e-07, 3.30067911516630e-07,
                  3.13429906260035e-07, 3.03720992821877e-07, 2.88634710657772e-07, 2.74799653104203e-07,
                  2.67996698449539e-07, 2.50877347511189e-07, 2.38160059940251e-07, 2.24474283108719e-07,
                  2.13162954474516e-07, 2.04690547648461e-07, 1.97697618138098e-07, 1.89927450984560e-07,
                  1.83938643504457e-07, 1.72762371458191e-07, 1.64211542935680e-07, 1.58424950852324e-07,
                  1.48938592041789e-07, 1.42641571367666e-07, 1.34572556308535e-07, 1.29430646707875e-07,
                  1.22186982111589e-07, 1.15755851008638e-07, 1.10503513257390e-07, 1.06783255252658e-07,
                  1.01277532057332e-07, 9.43621401994685e-08, 8.66895939014789e-08, 8.23475942103369e-08,
                  7.97010750236329e-08, 7.48238266736953e-08, 7.04990670080386e-08, 6.52992692480372e-08,
                  6.17550059214575e-08, 5.73278496908541e-08, 5.31377495252991e-08, 5.00311110386191e-08,
                  4.63971148128278e-08, 4.33219182688595e-08, 3.97138505763498e-08, 3.71520554399501e-08,
                  3.37006920901795e-08, 3.08539514317643e-08, 2.87646697479823e-08, 2.63504305446115e-08,
                  2.37999427855522e-08, 2.26860013245252e-08, 2.07936334332681e-08, 1.91024946637942e-08,
                  1.71944675795184e-08, 1.62698568387615e-08, 1.50620072583190e-08, 1.44180531321305e-08,
                  1.35820987957281e-08, 1.29454604124832e-08, 1.28282120623197e-08, 1.23396218153985e-08,
                  1.21356049534891e-08, 1.18671309527197e-08, 1.20677562631827e-08, 1.22190433261332e-08,
                  1.24970185552656e-08, 1.23250292614887e-08, 1.28894980268185e-08, 1.32419481042036e-08,
                  1.32836219702095e-08, 1.40207016066353e-08, 1.42720190651168e-08, 1.43011046999729e-08,
                  1.47083805268668e-08, 1.50885941818194e-08, 1.51494929643599e-08, 1.55160116772730e-08,
                  1.54338856281701e-08, 1.59034038815075e-08, 1.57449150174302e-08, 1.56965233255726e-08,
                  1.54552179687527e-08, 1.53323576980381e-08, 1.53362533641807e-08, 1.49360311905061e-08,
                  1.48058183017036e-08, 1.44744893660825e-08, 1.40426349594431e-08, 1.36678290350521e-08,
                  1.32187808076580e-08, 1.31226276165554e-08, 1.25431828789748e-08, 1.23085838994648e-08,
                  1.17589589882313e-08, 1.12252869636442e-08, 1.08940473409769e-08, 1.05443612856623e-08,
                  1.01453596802462e-08, 9.83780973879624e-09, 9.44304531580569e-09, 9.19552233955886e-09,
                  8.95100578193612e-09, 8.60956034442690e-09, 8.46217704007130e-09, 8.35243881831049e-09,
                  8.22177144249874e-09, 8.14217850702200e-09, 8.05408736615532e-09, 8.03754153554013e-09,
                  8.11531930744293e-09, 8.17660998599579e-09, 8.20165333874107e-09, 8.31174471659749e-09,
                  8.41420071579722e-09, 8.70405129860911e-09, 8.82685208964075e-09, 8.84609415341114e-09,
                  9.12490891707173e-09, 9.44775904868302e-09, 9.64971357160747e-09, 9.72401539043036e-09,
                  1.00187933936491e-08, 1.02678582540819e-08, 1.05104007125309e-08, 1.07460652729190e-08,
                  1.07871011375819e-08, 1.13239233386507e-08, 1.14653475222328e-08, 1.15296232228472e-08,
                  1.18196331828017e-08, 1.18536626984965e-08, 1.21385096165467e-08, 1.20915144977500e-08,
                  1.22568348906121e-08, 1.24253158753117e-08, 1.25372475115458e-08, 1.26193749899074e-08,
                  1.28427184390675e-08, 1.27432261895472e-08, 1.28462947972924e-08, 1.28228797202864e-08,
                  1.29973179406871e-08, 1.27921495227504e-08, 1.29075425248766e-08, 1.28995319056928e-08,
                  1.29709180973061e-08, 1.28791251861747e-08, 1.27825994117986e-08, 1.25591450387766e-08,
                  1.25037161511047e-08, 1.27707207778715e-08, 1.24419052183699e-08, 1.25334990197956e-08,
                  1.25267466697345e-08, 1.24055902914037e-08, 1.20883572914270e-08, 1.20073043632533e-08,
                  1.17584840588113e-08, 1.16727319594448e-08, 1.17705262750697e-08, 1.17615607735210e-08,
                  1.13581827572531e-08, 1.13368145754561e-08, 1.11384282499791e-08, 1.11123604009849e-08,
                  1.06350105487156e-08, 1.07806886417339e-08, 1.05623384704122e-08, 1.04610385989021e-08,
                  1.01872286308010e-08, 1.00197613484506e-08, 9.80916729595086e-09, 9.94106944424440e-09,
                  9.71844196047031e-09, 9.50948157130208e-09, 9.34881651187146e-09, 9.19857009634992e-09,
                  9.08593945946998e-09, 8.94666852394253e-09, 8.81584705546601e-09, 8.47887904490651e-09,
                  8.43763948323309e-09, 8.47578608706971e-09, 8.20805448408339e-09, 8.04959627803338e-09,
                  7.84022642398165e-09, 7.88581266629828e-09, 7.64107442233025e-09, 7.57222855187598e-09,
                  7.36665872514071e-09, 7.38253114771021e-09, 7.26505053330269e-09, 7.07223027787267e-09,
                  6.97021929587131e-09, 6.82425127515634e-09, 6.89736401900291e-09, 6.66992859851545e-09,
                  6.61460954851629e-09, 6.51181651707937e-09, 6.44508637143702e-09, 6.45610332520672e-09,
                  6.33046832788904e-09, 6.22176140330527e-09, 6.23598448275473e-09, 6.23021095482203e-09,
                  6.19798658376121e-09, 6.10641243808578e-09, 6.06554162741670e-09, 6.14635625989937e-09,
                  6.13081229415009e-09, 6.11704256352033e-09, 6.06576068736526e-09, 6.11832492212053e-09,
                  6.20357047068721e-09, 6.21936302905819e-09, 6.18616289930780e-09, 6.19894716262241e-09,
                  6.36989667130753e-09, 6.37804191636784e-09, 6.46874586300163e-09, 6.42734006284377e-09,
                  6.59468354611630e-09, 6.70432160192223e-09, 6.78514776354703e-09, 6.81921858533582e-09,
                  6.83336346702455e-09, 7.00721488220545e-09, 7.12715360212327e-09, 7.19884166791996e-09,
                  7.29298968200818e-09, 7.37593907234373e-09, 7.58409929532260e-09, 7.53692484699357e-09,
                  7.63296993221228e-09, 7.74074461662520e-09, 7.87269788886191e-09, 8.05635194592090e-09,
                  8.05375949411308e-09, 8.12503548049438e-09, 8.24422667999210e-09, 8.31708852186548e-09,
                  8.52765399339300e-09, 8.38559918116659e-09, 8.58277024682485e-09, 8.58890400572100e-09,
                  8.73539821148376e-09, 8.61320150986839e-09, 8.86869457819456e-09, 8.83553720407036e-09,
                  8.84036576883360e-09, 8.93678673155361e-09, 8.83537435622520e-09, 8.66191753336350e-09,
                  8.74620849243848e-09, 8.80683997372379e-09, 8.84845382469954e-09, 8.76622457210192e-09,
                  8.64224715794218e-09, 8.66401931722051e-09, 8.55409678838542e-09, 8.38508967371981e-09,
                  8.41196006075755e-09, 8.27836987488605e-09, 8.10045081013938e-09, 8.09115226926859e-09,
                  7.90874378055291e-09, 7.77347770899612e-09, 7.64843398071162e-09, 7.55662371538550e-09,
                  7.40679467685124e-09, 7.24472275254694e-09, 7.12644907886771e-09, 6.96680505735342e-09,
                  6.84188165505771e-09, 6.68927411177299e-09, 6.53581434145592e-09, 6.41730849205438e-09,
                  6.32676874873490e-09, 6.13973202133388e-09, 5.99921405689694e-09, 5.90849635617375e-09,
                  5.85470756505375e-09, 5.70703402873957e-09, 5.53367094089815e-09, 5.50358603053393e-09,
                  5.45976517378417e-09, 5.38562174726508e-09, 5.29361162951415e-09, 5.22379964705863e-09,
                  5.24084670383661e-09, 5.22610720569617e-09, 5.20665969878838e-09, 5.17826778495070e-09,
                  5.19715915338678e-09, 5.28765417450591e-09, 5.33341019142194e-09, 5.31596831456025e-09,
                  5.39105748724983e-09, 5.51586455101943e-09, 5.67045124414651e-09, 5.73225445695453e-09,
                  5.76281304203984e-09, 5.98635003146130e-09, 6.19189943243678e-09, 6.27766966135523e-09,
                  6.40576792111652e-09, 6.64312373074044e-09, 6.75145770650152e-09, 7.12153363492708e-09,
                  7.07716218402933e-09, 7.59847105842650e-09, 7.97625278320909e-09, 8.21153383547577e-09,
                  8.08484979314034e-09, 8.38121173281176e-09, 8.47795729324677e-09, 8.81052226335894e-09,
                  9.04825340298944e-09, 9.08938064330689e-09, 9.38435028109522e-09, 9.50563544636009e-09,
                  9.73347885002146e-09, 9.92784637557983e-09, 9.96571831108112e-09, 1.05311779049360e-08,
                  1.04903051005866e-08, 1.06203705674889e-08, 1.08197323533492e-08, 1.04997926013933e-08,
                  1.08516466217419e-08, 1.08861566269503e-08, 1.09685091289644e-08, 1.08684882552757e-08,
                  1.09582446029681e-08, 1.07842766136097e-08, 1.08480377409314e-08, 1.07428651399853e-08,
                  1.09526960615159e-08, 1.07352632196625e-08, 1.06191465323148e-08, 1.06236888636880e-08,
                  1.02460398270652e-08, 1.02834603855961e-08, 1.00371269282241e-08, 9.89008060986722e-09,
                  9.54797743998147e-09, 9.61963981017928e-09, 9.04470260689983e-09, 9.07945279478662e-09,
                  8.69997562122384e-09, 8.69057447081210e-09, 8.26653964572654e-09, 8.06627416330421e-09,
                  7.80509806063779e-09, 7.51186615411658e-09, 7.25840353036627e-09, 7.09361384584830e-09,
                  6.82831848518548e-09, 6.56243839778335e-09, 6.34295305289336e-09, 6.04666269223983e-09,
                  5.93682671663685e-09, 5.74446355164421e-09, 5.54973502276983e-09, 5.31688627800498e-09,
                  5.20610701051850e-09, 5.08001443598997e-09, 5.05519242097039e-09, 4.93162440245895e-09,
                  4.78552802877058e-09, 4.79345453693508e-09, 4.78917127095902e-09, 4.79257973561460e-09,
                  4.76655689776503e-09, 4.80418929575097e-09, 4.93527232381691e-09, 5.07231797107576e-09,
                  5.07825585610543e-09, 5.27191644419243e-09, 5.42054782750199e-09, 5.62482196680140e-09,
                  5.80128031119815e-09, 6.01830756240572e-09, 6.28587818034269e-09, 6.62412846808276e-09,
                  6.73340052065807e-09, 7.11722751835444e-09, 7.35532647050431e-09, 7.71416808300485e-09,
                  8.17955239988027e-09, 8.39964529178026e-09, 8.66542660211900e-09, 8.92971638395389e-09,
                  9.53123352138477e-09, 9.61954499589397e-09, 1.00376030890240e-08, 1.02678353165108e-08,
                  1.06551591120823e-08, 1.10958254039842e-08, 1.11447374735411e-08, 1.14744328850929e-08,
                  1.15167847714678e-08, 1.19266276784467e-08, 1.22362183035677e-08, 1.22784121563390e-08,
                  1.23182858107873e-08, 1.24762715605983e-08, 1.26782535392525e-08, 1.29397619399789e-08,
                  1.29797028046751e-08, 1.30276880095548e-08, 1.27134958989925e-08, 1.28926520351367e-08,
                  1.27201683728450e-08, 1.26751598660526e-08, 1.24890319147621e-08, 1.25375848975444e-08,
                  1.22260465221358e-08, 1.20334796208192e-08, 1.19448287165050e-08, 1.18858189534083e-08,
                  1.13985137035275e-08, 1.10919126934910e-08, 1.08717275062873e-08, 1.06618258633244e-08,
                  1.03052339160006e-08, 9.90114622220627e-09, 9.75503435268087e-09, 9.17658172007369e-09,
                  8.66843837636719e-09, 8.61348099566140e-09, 8.03208697817769e-09, 7.67325341787941e-09,
                  7.36643203484623e-09, 7.05963267193484e-09, 6.75443328963404e-09, 6.50977730092499e-09,
                  6.05833288255153e-09, 5.88000514723227e-09, 5.68359185216403e-09, 5.40299237832263e-09,
                  5.12948986417307e-09, 4.99264114848373e-09, 4.82457852698581e-09, 4.71325995827692e-09,
                  4.56436306277787e-09, 4.44468687548332e-09, 4.45690397514216e-09, 4.43844524480389e-09,
                  4.46350425181594e-09, 4.43285197193375e-09, 4.51301338475480e-09, 4.63395465720549e-09,
                  4.78307798514555e-09, 4.90559122539794e-09, 5.05896769629320e-09, 5.30638960773179e-09,
                  5.50620149506042e-09, 5.71924053555511e-09, 6.02402919224847e-09, 6.13690671988587e-09,
                  6.62343066818935e-09, 6.83619643296632e-09, 7.03556867018822e-09, 7.47615935748243e-09,
                  7.79938513696424e-09, 8.20461176873868e-09, 8.36951360564259e-09, 8.87511596941587e-09,
                  8.96317600856258e-09, 9.36884377314376e-09, 9.44881371016363e-09, 9.84826687485888e-09,
                  1.01067505390981e-08, 1.04865512538349e-08, 1.06742911302100e-08, 1.08826804772582e-08,
                  1.07988655370995e-08, 1.10489480715200e-08, 1.11055704416854e-08, 1.10603971025097e-08,
                  1.10018346780983e-08, 1.09139009949028e-08, 1.09566689303234e-08, 1.13830636789298e-08,
                  1.12998127330269e-08, 1.12280609118899e-08, 1.09986542189594e-08, 1.05601915982285e-08,
                  1.01652518484794e-08, 1.00009039306147e-08, 9.94635035435038e-09, 9.87834071074689e-09,
                  9.67543651388748e-09, 9.48667508095968e-09, 9.52165756328639e-09, 8.82192675636523e-09,
                  8.49250115127243e-09, 8.07158319281818e-09, 7.79319831868151e-09, 7.44868801987736e-09,
                  7.06343528506092e-09, 6.97039510804949e-09, 6.71626396887560e-09, 6.72576427001867e-09,
                  6.03171045432870e-09, 5.87240298484062e-09, 5.68176916797240e-09, 5.67641154128319e-09,
                  5.26312509202078e-09, 5.04807718443033e-09, 4.99790111811965e-09, 5.05659178386406e-09,
                  4.81835745270881e-09, 4.59081163930200e-09, 4.57714811555838e-09, 4.57078446230199e-09,
                  4.53998782144989e-09, 4.43289735546490e-09, 4.40486489459850e-09, 4.42317316988629e-09,
                  4.45853802563628e-09, 4.40110475476902e-09, 4.37467329232380e-09, 4.41037858050479e-09,
                  2.21845864714005e-09]

    psd = sig.welch(segment,nperseg = NFFT / 2,nfft = NFFT)

    npsd = psd[1] / sum(psd[1])

    fv = max(np.abs(npsd-meanClnPSD))

    return fv
