#!/usr/bin/env python

# Created by Raul Peralta-Lozada (28/09/17)
import pandas as pd


def contratos_por_proveedor(df):
    """Por cada unidad compradora calcula el número de contratos por
    por proveedor diferente
    """
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    # Proveedores distintos
    pocs_distintos = monto_por_contrato.groupby('CLAVEUC').PROVEEDOR_CONTRATISTA.nunique()
    pocs_distintos = pocs_distintos.reset_index()
    pocs_distintos = pocs_distintos.rename(
      columns={'PROVEEDOR_CONTRATISTA': 'proveedores_distintos'})
    # procedimientos distintos
    procedimientos_distintos = monto_por_contrato.groupby('CLAVEUC').NUMERO_PROCEDIMIENTO.nunique()
    procedimientos_distintos = procedimientos_distintos.reset_index()
    procedimientos_distintos = procedimientos_distintos.rename(
      columns={'NUMERO_PROCEDIMIENTO': 'conteo_procedimientos'})
    # Numero de contratos
    contratos_total = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO']).CODIGO_CONTRATO.nunique()
    contratos_total = contratos_total.reset_index()
    contratos_total = contratos_total.rename(columns={'CODIGO_CONTRATO': 'conteo_contratos'})
    contratos_total = contratos_total.groupby('CLAVEUC', as_index=False).conteo_contratos.sum()
    df_feature = pd.merge(pocs_distintos, contratos_total, on='CLAVEUC', how='inner')
    df_feature = pd.merge(df_feature, procedimientos_distintos, on='CLAVEUC', how='inner')
    df_feature = df_feature.assign(
        contratos_por_proveedor=df_feature.conteo_contratos.divide(df_feature.proveedores_distintos)
    )
    df_feature = df_feature.loc[:, ['CLAVEUC', 'contratos_por_proveedor']]
    return df_feature


def porcentaje_procedimientos_por_tipo(df):
    """Por cada unidad compradora calcula el porcentaje de procedimientos por tipo"""
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA', 'NUMERO_PROCEDIMIENTO',
         'CODIGO_CONTRATO', 'TIPO_PROCEDIMIENTO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    conteo_tipos = monto_por_contrato.groupby(
        ['CLAVEUC', 'TIPO_PROCEDIMIENTO']
    ).NUMERO_PROCEDIMIENTO.nunique().reset_index()
    conteo_tipos = conteo_tipos.pivot(
        index='CLAVEUC', columns='TIPO_PROCEDIMIENTO',
        values='NUMERO_PROCEDIMIENTO'
    ).fillna(0)
    total_procedimientos = conteo_tipos.sum(axis=1)
    conteo_tipos = conteo_tipos * 100
    conteo_tipos = conteo_tipos.divide(total_procedimientos, axis='index')
    conteo_tipos = conteo_tipos.rename(
        columns={
            col: 'pc_procedimientos_' + col.replace(' ', '_').lower()
            for col in conteo_tipos.columns
        }
    )
    conteo_tipos = conteo_tipos.reset_index()
    conteo_tipos.columns.name = ''
    return conteo_tipos


def porcentaje_monto_tipo_procedimiento(df):
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO', 'TIPO_PROCEDIMIENTO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    monto_tipos = monto_por_contrato.groupby(
        ['CLAVEUC', 'TIPO_PROCEDIMIENTO'], as_index=False
    ).IMPORTE_PESOS.sum()
    monto_tipos = monto_tipos.pivot(
        index='CLAVEUC', columns='TIPO_PROCEDIMIENTO',
        values='IMPORTE_PESOS'
    ).fillna(0)
    total_montos = monto_tipos.sum(axis=1)
    monto_tipos = monto_tipos * 100
    monto_tipos = monto_tipos.divide(total_montos, axis='index')
    monto_tipos = monto_tipos.rename(
        columns={
            col: 'pc_monto_' + col.replace(' ', '_').lower()
            for col in monto_tipos.columns
        }
    )
    monto_tipos = monto_tipos.reset_index()
    monto_tipos.columns.name = ''
    return monto_tipos


def importe_promedio_por_contrato(df):
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    contratos_total = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO']).CODIGO_CONTRATO.nunique()
    contratos_total = contratos_total.reset_index()
    contratos_total = contratos_total.rename(columns={'CODIGO_CONTRATO': 'conteo_contratos'})
    contratos_total = contratos_total.groupby('CLAVEUC', as_index=False).conteo_contratos.sum()

    monto_uc_contratos = monto_por_contrato.groupby(
        ['CLAVEUC', 'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'], as_index=False
    ).IMPORTE_PESOS.sum()
    monto_uc_contratos = monto_uc_contratos.groupby('CLAVEUC', as_index=False).IMPORTE_PESOS.sum()

    df_feature = pd.merge(monto_uc_contratos, contratos_total, on='CLAVEUC', how='inner')
    df_feature = df_feature.assign(
        monto_contrato_promedio=df_feature.IMPORTE_PESOS.divide(df_feature.conteo_contratos)
    )
    df_feature = df_feature.drop('conteo_contratos', axis=1)
    df_feature = df_feature.rename(columns={'IMPORTE_PESOS': 'monto_total'})
    df_feature = df_feature.loc[:, ['CLAVEUC', 'monto_contrato_promedio']]
    return df_feature


def calcular_IHH_ID_contratos(df):
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    contratos_uc_poc = monto_por_contrato.groupby(
        ['CLAVEUC', 'PROVEEDOR_CONTRATISTA', 'NUMERO_PROCEDIMIENTO'],
    ).CODIGO_CONTRATO.nunique()
    contratos_uc_poc = contratos_uc_poc.reset_index()
    contratos_uc_poc = contratos_uc_poc.groupby(
        ['CLAVEUC', 'PROVEEDOR_CONTRATISTA'], as_index=False
    ).CODIGO_CONTRATO.sum()
    contratos_uc = contratos_uc_poc.groupby(
        'CLAVEUC', as_index=False
    ).CODIGO_CONTRATO.sum()
    contratos_uc = contratos_uc.rename(
        columns={'CODIGO_CONTRATO': 'contratos_por_uc'}
    )
    contratos_uc_poc = pd.merge(
        contratos_uc_poc, contratos_uc, how='left', on='CLAVEUC'
    )
    contratos_uc_poc = contratos_uc_poc.assign(
        Share=(contratos_uc_poc.CODIGO_CONTRATO.divide(contratos_uc_poc.contratos_por_uc) * 100)
    )
    contratos_uc_poc = contratos_uc_poc.assign(
        IHH_contratos=contratos_uc_poc.Share ** 2
    )
    contratos_uc_poc = contratos_uc_poc.drop(
        ['contratos_por_uc', 'Share'], axis=1)
    # IHH por uc
    uc_IHH = contratos_uc_poc.groupby(
        'CLAVEUC', as_index=False).IHH_contratos.sum()
    uc_IHH = uc_IHH.rename(columns={'IHH_contratos': 'IHH_total_contratos'})

    # ID por uc
    contratos_uc_poc = pd.merge(
        contratos_uc_poc, uc_IHH, on='CLAVEUC', how='inner'
    )
    contratos_uc_poc = contratos_uc_poc.assign(
        ID_contratos=(
            contratos_uc_poc.IHH_contratos.divide(contratos_uc_poc.IHH_total_contratos)
        )
    )
    contratos_uc_poc = contratos_uc_poc.assign(
        ID_contratos=(contratos_uc_poc.ID_contratos * 100) ** 2
    )
    uc_ID = contratos_uc_poc.groupby('CLAVEUC', as_index=False).ID_contratos.sum()
    uc_ID = uc_ID.rename(columns={'ID_contratos': 'ID_total_contratos'})
    # final join
    df_feature = pd.merge(uc_IHH, uc_ID, on='CLAVEUC', how='inner')
    return df_feature


def calcular_IHH_ID_monto(df):
    monto_por_contrato = df.groupby(
        ['DEPENDENCIA', 'CLAVEUC', 'PROVEEDOR_CONTRATISTA',
         'NUMERO_PROCEDIMIENTO', 'CODIGO_CONTRATO'],
        as_index=False
    ).IMPORTE_PESOS.sum()
    monto_uc_poc = monto_por_contrato.groupby(
        ['CLAVEUC', 'PROVEEDOR_CONTRATISTA'], as_index=False
    ).IMPORTE_PESOS.sum()
    monto_uc = monto_uc_poc.groupby(
        'CLAVEUC', as_index=False
    ).IMPORTE_PESOS.sum()
    monto_uc = monto_uc.rename(columns={'IMPORTE_PESOS': 'monto_por_uc'})
    monto_uc_poc = pd.merge(monto_uc_poc, monto_uc, how='left', on='CLAVEUC')
    monto_uc_poc = monto_uc_poc.assign(
        Share=(monto_uc_poc.IMPORTE_PESOS.divide(monto_uc_poc.monto_por_uc) * 100)
    )
    monto_uc_poc = monto_uc_poc.assign(
        IHH_monto=monto_uc_poc.Share**2
    )
    uc_IHH = monto_uc_poc.groupby(
        'CLAVEUC', as_index=False).IHH_monto.sum()
    uc_IHH = uc_IHH.rename(columns={'IHH_monto': 'IHH_total_monto'})
    # ID por uc
    monto_uc_poc = pd.merge(monto_uc_poc, uc_IHH, on='CLAVEUC', how='inner')
    monto_uc_poc = monto_uc_poc.assign(
        ID_monto=(
            monto_uc_poc.IHH_monto.divide(monto_uc_poc.IHH_total_monto)
        )
    )
    monto_uc_poc = monto_uc_poc.assign(
        ID_monto=(monto_uc_poc.ID_monto * 100) ** 2
    )
    uc_ID = monto_uc_poc.groupby('CLAVEUC', as_index=False).ID_monto.sum()
    uc_ID = uc_ID.rename(columns={'ID_monto': 'ID_total_monto'})
    # final join
    df_feature = pd.merge(uc_IHH, uc_ID, on='CLAVEUC', how='inner')
    return df_feature
