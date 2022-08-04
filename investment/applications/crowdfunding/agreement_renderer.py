"""
Client product agreement renderer
"""

from products.agreement_render import BaseRenderer
from common.formats import decimal_format

class ClientAgreementRenderer(BaseRenderer):

    """
    Client agreement rendering according to a template
    """

    @classmethod
    def content_data(cls, user, extra_args=None):
        """
        Data to be rendered related to the available tags
        """
        client = getattr(user, 'client')

        if client:

            address = []
            address.append(client.address)
            if client.number:
                address.append(f'numero {client.number}')
            if client.complement:
                address.append(f'complemento {client.complement}')
            if client.zip_code:
                address.append(f'cep {client.zip_code}')
            address.append(f'na cidade de {client.city}')
            address.append(f'{client.get_state_display()}')

            address_str = ", ".join(address)

            value = extra_args['value']
            if isinstance(value, float):
                value = decimal_format(value)

            return {
                'nome': user.get_full_name(),
                'email': user.email,
                'endereco': address_str,
                'telefone': client.phone,
                'cpf_cliente': client.cpf,
                'nome_da_empresa': client.company_name,
                'cnpj': client.cnpj,
                'valor_do_contrato': extra_args['value'],
            }
        else:
            return dict()

    @classmethod
    def preview_data(cls):
        """
        Fake Data to be rendered as preview
        """

        return {
            'nome': 'José Antônio da Silva',
            'email': 'joseantonio@email.com',
            'endereco': 'Avenida Presidente Getúlio Vargas, número 1000, Ribeirão Preto, São Paulo',
            'telefone': '(16) 1234-4567',
            'cpf_cliente': '123.456.789-10',
            'nome_da_empresa': 'Comércio e distribuição de mercadorias',
            'cnpj': '38.874.787/0001-93',
            'valor_do_contrato': '5.000,00',
        }

    @classmethod
    def available_tags(cls):
        """
        Available tags
        """
        return ['nome', 'email', 'endereco', 'telefone', 'cpf_cliente', 'nome_da_empresa', 'cnpj', 'valor_do_contrato', 'valor_do_fundo']
