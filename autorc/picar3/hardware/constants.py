'''
    Raspberry model revision
    https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md
'''


RPI_COM_1 = 'Compute Module 1'
RPI_MODEL_ZERO = 'Zero'
RPI_MODEL_A = '1 Model A'
RPI_MODEL_AP = '1 Model A+'
RPI_MODEL_B = '1 Model B'
RPI_MODEL_BP = '1 Model B+'
RPI_2_MODEL_B = '2 Model B'
RPI_3_MODEL_B = '3 Model B'
RPI_3_MODEL_BP = '3 Model B+'


RPI_REVISION_CM1 = {'0011', '0014'}
RPI_REVISION_ZERO = {'900092', '920092', '900093', '9000c1', '920093'}
RPI_REVISION_1_MODULE_A = {'0007', '0008', '0009'}
RPI_REVISION_1_MODULE_AP = {'0012', '0015', '900021'}
RPI_REVISION_1_MODULE_B = {'Beta', '0002', '0003', '0004', '0005', '0006',
                           '000d', '000e', '000f'}
RPI_REVISION_1_MODULE_BP = {'0010', '0013', '900032'}
RPI_REVISION_2_MODULE_B = {'a01041', 'a21041', 'a01040', 'a22042'}
RPI_REVISION_3_MODULE_B = {'a02082', 'a22082', 'a32082', 'a52082'}
RPI_REVISION_3_MODULE_BP = {'a020d3'}

RPI_MODEL_REVISION = {
    RPI_COM_1: RPI_REVISION_CM1,
    RPI_MODEL_ZERO: RPI_REVISION_ZERO,
    RPI_MODEL_A: RPI_REVISION_1_MODULE_A,
    RPI_MODEL_AP: RPI_REVISION_1_MODULE_AP,
    RPI_MODEL_B: RPI_REVISION_1_MODULE_B,
    RPI_MODEL_BP: RPI_REVISION_1_MODULE_BP,
    RPI_2_MODEL_B: RPI_REVISION_2_MODULE_B,
    RPI_3_MODEL_B: RPI_REVISION_3_MODULE_B,
    RPI_3_MODEL_BP: RPI_REVISION_3_MODULE_BP,
}

RPI_REVISION_MODEL = {}     # Reverse revison -> model lookup
for k, rev in RPI_MODEL_REVISION.items():
    for code in rev:
        RPI_REVISION_MODEL[code] = k
