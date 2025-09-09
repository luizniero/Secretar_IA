# tools.py
from langchain.tools import tool
import datetime
import os.path

# Importações para a API do Google Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Se modificar esses escopos, delete o arquivo token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Função auxiliar para autenticação, não um método de classe
def _get_google_calendar_service():
    """Autentica com a API do Google Calendar e retorna o objeto de serviço."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("calendar", "v3", credentials=creds)

class Ferramentas:
    # Removemos a inicialização do service no __init__ pois agora ele é obtido por chamada na tool
    # def __init__(self):
    #    self.service = self._get_google_calendar_service()

    @tool
    def consulta_disponibilidade(data: str, servico: str) -> str:
        """
        Verifica a disponibilidade de horários para um serviço em uma data específica na agenda do Google.
        Formato da data esperado: AAAA-MM-DD.
        Retorna uma string com os horários disponíveis ou uma mensagem de indisponibilidade.
        """
        try:
            # Obtém o serviço diretamente dentro da tool, garantindo que seja sempre validado
            service = _get_google_calendar_service()

            data_obj = datetime.datetime.strptime(data, "%Y-%m-%d").date()
            
            time_min = datetime.datetime(data_obj.year, data_obj.month, data_obj.day, 8, 0, 0).isoformat() + "Z" # 8 AM UTC
            time_max = datetime.datetime(data_obj.year, data_obj.month, data_obj.day, 18, 0, 0).isoformat() + "Z" # 6 PM UTC

            events_result = (
                service.events() # Usamos o 'service' obtido aqui
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                return f"Não encontrei eventos agendados para {data}. Parece que há boa disponibilidade para {servico} neste dia!"
            
            available_slots = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                summary = event.get("summary", "Nenhum Título")
                available_slots.append(f"- {summary} de {start.split('T')[1][:5]} a {end.split('T')[1][:5]}")
            
            return f"Eventos encontrados para {data}: \n" + "\n".join(available_slots) + "\nCom base nisso, você pode agendar {servico} em horários que não estejam conflitantes."

        except ValueError:
            return "Formato de data inválido. Por favor, use AAAA-MM-DD."
        except HttpError as error:
            return f"Ocorreu um erro na API do Google Calendar ao verificar disponibilidade: {error}"
        except Exception as e:
            return f"Ocorreu um erro inesperado ao verificar a disponibilidade: {e}"

    @tool
    def agenda_consulta(data: str, horario: str, servico: str, nome_cliente: str) -> str:
        """
        Agenda um compromisso para um serviço em uma data e horário específicos na agenda do Google.
        Formato da data esperado: AAAA-MM-DD. Formato do horário esperado: HH:MM.
        Retorna uma string de confirmação ou erro.
        """
        try:
            # Obtém o serviço diretamente dentro da tool
            service = _get_google_calendar_service()

            start_datetime_str = f"{data} {horario}"
            start_time = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
            end_time = start_time + datetime.timedelta(hours=1)

            event = {
                'summary': f'{servico} - {nome_cliente}',
                'description': f'Agendamento para {servico} com {nome_cliente}',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            event = service.events().insert(calendarId='primary', body=event).execute() # Usamos o 'service' obtido aqui
            
            return f"Agendamento confirmado! {servico} para {nome_cliente} em {data} às {horario}. Link do evento: {event.get('htmlLink')}"

        except ValueError:
            return "Formato de data ou hora inválido. Use AAAA-MM-DD para data e HH:MM para hora."
        except HttpError as error:
            return f"Ocorreu um erro na API do Google Calendar ao agendar: {error}. Verifique suas permissões ou se o calendário 'primary' existe."
        except Exception as e:
            return f"Ocorreu um erro inesperado ao agendar: {e}"