import io
import os
import re
import time
import datetime
import pandas as pd
import csv, json

from lib.api_cxpostal import ApiCxPostal


class Sender:
    datasets = []
    path_dataset = "data"
    n_sockets = 40  # número de conexões simultâneas push
    n_destinatario = 250000  # número de destinatarios da caixa postal por requisicao (max 500000)


    def __init__(self):
        self.datasets = [os.path.abspath(os.path.join(self.path_dataset, f)) for f in os.listdir(self.path_dataset) if
                         f.endswith('.csv')]

    def run(self):
        self.send_caixa()
        ti = time.time()
        print(datetime.datetime.now())
        print(time.time() - ti)
        return None

    def send_caixa(self):

        ti = time.time()
        for dataset in self.datasets:

            config = {}
            if not os.path.exists(f"{dataset}.json"):
                return False

            with open(f"{dataset}.json", "r") as f:
                config = json.load(f)

            if not {"api_key", "env", "assunto", "template_id", "versao", "tags"}.issubset(config.keys()):
                return False

            api = ApiCxPostal("", "", config["api_key"], config["env"])

            t0 = api.get_template_payload_msg(2)
            t0["template_id"] = int(config["template_id"])
            t0["versao"] = int(config["versao"])
            t0["assunto"] = config["assunto"]
            t0["has_push"] = True

            list_cpf = pd.read_csv(dataset, sep=',', encoding='utf-8-sig', dtype=str)
            if not len(list_cpf) or 'cpf' not in list_cpf.columns:
                return False

            list_cpf['cpf'] = list_cpf['cpf'].dropna()
            list_cpf['cpf'] = list_cpf['cpf'].astype(str).apply(lambda x: re.sub(r'\D', '', x))
            list_cpf['cpf'] = list_cpf['cpf'].apply(lambda x: x.zfill(11))

            list_cpf = [list_cpf[i:i + self.n_destinatario] for i in range(0, len(list_cpf), self.n_destinatario)]

            for index, sublist_cpf in enumerate(list_cpf):
                print(f"lote: {index + 1}/{len(list_cpf)} - tempo: {time.time() - ti}")
                t_msg = t0.copy()
                destinatarios = []
                for i, item in sublist_cpf.iterrows():
                    tag = {}
                    for t in config['tags']:
                        if t in item.keys():
                            tag[t] = item[t]
                        else:
                            tag[t] = ""
                    destinatarios.append({"cpf": item['cpf'], "tags": tag})

                t_msg["destinatarios"] = destinatarios
                # print(t_msg)
                log = api.send([t_msg])

                with open(f'{dataset}.out_msg{time.time()}.log', 'w') as f:
                    w = csv.writer(f)
                    for msg in log:
                        w.writerow(msg.values())

            self.log_concat(f"{dataset}.out_msg")
            self.log_stats_caixa(f"{dataset}.out_msg.log")

        return None

    def send_caixa_evento(self, api, template_id, versao, assunto):

        t0 = api.get_template_payload_msg(2)
        t0["template_id"] = template_id
        t0["versao"] = versao
        t0["assunto"] = assunto

        ti = time.time()

        for dataset in self.datasets:
            list_cpf = self.task.get_cpf_from_dataset(dataset)
            if not len(list_cpf):
                return False

            # for cpf in list_cpf:
            list_cpf = [list_cpf[i:i + self.n_destinatario] for i in range(0, len(list_cpf), self.n_destinatario)]
            for index, sublist_cpf in enumerate(list_cpf):
                print(f"lote: {index + 1}/{len(list_cpf)} - tempo: {time.time() - ti}")
                t_msg = t0.copy()
                destinatarios = []
                for cpf in sublist_cpf:
                    destinatarios.append({"cpf": cpf, "tags": {"nome": ""}})
                    # destinatarios.append({"cpf": cpf, "tags": {'nome_dinamico2':'teste'}})

                t_msg["destinatarios"] = destinatarios
                log = api.send([t_msg])

                with open(f'data/out_msg_{time.time()}.csv', 'w') as f:
                    w = csv.writer(f)
                    for msg in log:
                        w.writerow(msg.values())

        return None

    def log_concat(self, prefix):
        out_push = [os.path.abspath(os.path.join(self.path_dataset, f)) for f in os.listdir(self.path_dataset) if
                    f.startswith(prefix) and f.endswith('.log')]
        out_push.sort()
        with open(f"{prefix}.log", 'w') as log:
            log.write("start,end,status,message,request,response_status,response_json,response_text\n")
            for out in out_push:
                with open(out) as outlog:
                    log.write(outlog.read())

    def log_stats_caixa(self, path):
        data = pd.read_csv(path, sep=',', encoding='utf-8-sig')
        obj = {"sucessos": 0, "falhas": 0, "falha_detalhe": {}}
        for item in data['response_json'].tolist():
            try:
                x = json.loads(item.replace("'", '"'))
                if not all(prop in x.keys() for prop in ['sucessos', 'falhas']):
                    continue
                obj["sucessos"] += len(x['sucessos'])
                for falha in x['falhas']:
                    obj["falhas"] += len(falha['cpfs'])
                    if falha['motivo'] in obj["falha_detalhe"].keys():
                        total = obj["falha_detalhe"][falha['motivo']] + len(falha['cpfs'])
                        obj["falha_detalhe"].update({falha['motivo']: total})
                    else:
                        obj["falha_detalhe"].update({falha['motivo']: len(falha['cpfs'])})
            except Exception as e:
                # print(e)
                continue

        print("--------------STATS_CAIXA_POSTAL--------------")
        print("SUCESSO:                             ", obj["sucessos"])
        print("FALHA:                               ", obj["falhas"])
        for key in obj["falha_detalhe"].keys():
            print(f"  {key}:\t\t\t\t", obj["falha_detalhe"][key])

        return obj


Sender().run()
