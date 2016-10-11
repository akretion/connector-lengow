# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


class SetUpLengowBase(common.TransactionCase):
    """ Base class - Test the imports from a Lengow Mock.
    """
    def _configure_mock_request(self, key, mock_request):
        data = self.json_data
        mock_request.return_value.status_code = data[key]['status_code']
        mock_request.return_value.json.return_value = data[key]['json']
        return mock_request

    def setUp(self):
        super(SetUpLengowBase, self).setUp()
        self.backend_model = self.env['lengow.backend']
        self.catalogue_model = self.env['lengow.catalogue']
        self.marketplace_model = self.env['lengow.market.place']
        self.bind_wizard_model = self.env['lengow.product.binding.wizard']
        self.unbind_wizard_model = self.env['lengow.product.unbinding.wizard']
        self.product_bind_model = self.env['lengow.product.product']

        self.session = ConnectorSession(self.env.cr, self.env.uid,
                                        context=self.env.context)
        self.warehouse = self.env.ref('stock.warehouse0')
        self.post_method = 'openerp.addons.lengowerpconnect.models'\
                           '.adapter.requests.post'
        self.get_method = 'openerp.addons.lengowerpconnect.models'\
                          '.adapter.requests.get'
        self.json_data = {}


class SetUpLengowBase20(SetUpLengowBase):

    def setUp(self):
        super(SetUpLengowBase20, self).setUp()
        self.backend = self.backend_model.create(
            {'name': 'Test Lengow',
             'version': '2.0',
             'location': 'http://anyurl',
             'id_client': 'a4a506440102b8d06a0f63fdd1eadd5f',
             'warehouse_id': self.warehouse.id}
        )

        self.catalogue = self.catalogue_model.create(
            {'name': 'Test Lengow Catalogue',
             'backend_id': self.backend.id,
             'product_ftp': False,
             'product_filename': 'products.csv',
             'warehouse_id': self.warehouse.id})
        self.json_data = {
            'orders': {
                'status_code': 200,
                'json': {
                    "statistics": {
                        "-ip": "185.61.176.129",
                        "-server": "Oxalide",
                        "-timeGenerated": "2016-10-10 10:59:13.582742",
                        "-version": "1.0",
                        "countCommandes": "431",
                        "countCommandesAmazon": "283",
                        "countCommandesRueducommerce": "4",
                        "countCommandesPriceminister": "1",
                        "countCommandesCdiscount": "110",
                        "commandes": {
                            "commande": [{
                                "marketplace": "Amazon",
                                "idFlux": "23999",
                                "status": "accept",
                                "com_id": "5541-2121515-6705141",
                                "com_mrid": "5498-2121515-68905141",
                                "com_refid": "9804-2121515-6705141",
                                "com_external_id": "789999",
                                "com_payement_date": "2016-10-01",
                                "com_payement_heure": "04:51:24",
                                "com_purchase_date": "2016-10-01",
                                "com_purchase_heure": "04:51:24",
                                "com_fact_nom": "Bahadir AAAA",
                                "com_fact_email": "AAAA@marketplace.amazon.de",
                                "com_fact_adresse": "Römerstraße 19a",
                                "com_fact_adresse_complement": " Bayern",
                                "com_fact_cp": "93352",
                                "com_fact_ville": "Rohr",
                                "com_fact_pays": "DE",
                                "com_fact_pays_iso": "DE",
                                "com_fact_telephone_home": "00000089492",
                                "com_fact_full": "AAA lengow 44000 Nantes",
                                "liv_fact_nom": "Bahadir AAAA",
                                "liv_fact_adresse": "AAA Lengow",
                                "liv_fact_adresse_complement": " Bayern",
                                "liv_fact_cp": "93352",
                                "liv_fact_ville": "Rohr",
                                "liv_fact_pays": "DE",
                                "liv_fact_pays_iso": "DE",
                                "liv_fact_telephone_home": "0000089492",
                                "liv_fact_full": "AAA Lengow 44000 Nantes",
                                "com_montant_commande": "105.85",
                                "com_montant_tax": "0.00",
                                "com_nb_article": "1",
                                "com_shipping": "5.9",
                                "com_shipping_description": "Standard",
                                "com_commission": "0.0",
                                "com_frais_traitement": "0",
                                "com_shipped_date": "2016-10-01 09:32:16",
                                "com_currency": "EUR",
                                "com_deliveringByMarketPlace": "0",
                                "panier": {
                                    "nb_orders": "1",
                                    "produits": {
                                        "produit": {
                                            "id": "0000_33544",
                                            "titre": "Pantalon G-star rovic"
                                                     " slim, micro stretch "
                                                     "twill GS Dk Fig Taille"
                                                     " W29/L32",
                                            "category": "Accueil > HOMME > "
                                                        "JEANS/PANTALONS > "
                                                        "PANTALONS",
                                            "url_produit": "http://www.Lengow."
                                                           "com/product.php?id"
                                                           "\\_product=11199",
                                            "url_image": "http://www.lengow."
                                                         "com/img/p/11199-421"
                                                         "04-large.jpg",
                                            "sku": "111111_33544",
                                            "qt": "1",
                                            "prix": "99.95",
                                            "prix_unitaire": "99.95"}}}},
                                         {
                                "marketplace": "Rueducommerce",
                                "idFlux": "99927",
                                "status": "shipped",
                                "com_id": "99924234",
                                "com_mrid": "MOR-DD135M2569999",
                                "com_refid": "999999244",
                                "com_external_id": "99987",
                                "com_payement_date": "2016-10-02",
                                "com_payement_heure": "09:54:03",
                                "com_purchase_date": "2016-10-02",
                                "com_purchase_heure": "09:54:03",
                                "com_fact_civilite": "M",
                                "com_fact_nom": "Lengow",
                                "com_fact_prenom": "Fabien",
                                "com_fact_email": "Lengow@sc.rueducommerce."
                                                  "com",
                                "com_fact_adresse": "2 rue la vermeillade",
                                "com_fact_cp": "44000",
                                "com_fact_ville": "Nantes",
                                "com_fact_pays": "France",
                                "com_fact_pays_iso": "FR",
                                "com_fact_telephone_home": "09999978878",
                                "com_fact_full": "Lengow 44000 Nantes ",
                                "liv_fact_nom": "Lengow",
                                "liv_fact_civilite": "M",
                                "liv_fact_prenom": "Lengow",
                                "liv_fact_email": "Lengow@sc.rueducommerce."
                                                  "com",
                                "liv_fact_adresse": "Lengow 44000 Nantes",
                                "liv_fact_adresse_complement": " mobile: "
                                                               "09999933185",
                                "liv_fact_cp": "44000",
                                "liv_fact_ville": "Nantes",
                                "liv_fact_pays": "France",
                                "liv_fact_pays_iso": "FR",
                                "liv_fact_telephone_home": "099999169",
                                "liv_fact_full": "Lengow 44000 Nantes  mobile:"
                                                 " 0999933185 France",
                                "com_montant_commande": "98.99",
                                "com_nb_article": "1",
                                "com_shipping": "0.0",
                                "com_commission": "0.0",
                                "com_frais_traitement": "0",
                                "com_type_livraison": "Colissimo",
                                "com_currency": "EUR",
                                "com_deliveringByMarketPlace": "0",
                                "panier": {
                                    "nb_orders": "1",
                                    "produits": {
                                        "produit": {
                                            "id": "9999_27951",
                                            "titre": "Pantalon Treillis Japan"
                                                     " Rags Mirador gris "
                                                     "Couleur Gris Taille 33",
                                            "category": "Accueil > HOMME > "
                                                        "JEANS/PANTALONS > "
                                                        "PANTALONS",
                                            "url_produit": "http://www.lengow."
                                                           "com/product.php?id"
                                                           "\\_product=99996",
                                            "url_image": "http://www.lengow."
                                                         "com/img/p/9999-52267"
                                                         "-large.jpg",
                                            "sku": "9999\\_279991",
                                            "qt": "1",
                                            "marque": "Japan Rags",
                                            "prix": "98.99",
                                            "prix_unitaire": "98.99"}
                                    }
                                }
                            }]
                        }
                    }
                }}}


class SetUpLengowBase30(SetUpLengowBase):

    def setUp(self):
        super(SetUpLengowBase30, self).setUp()
        self.backend = self.backend_model.create(
            {'name': 'Test Lengow',
             'version': '3.0',
             'location': 'http://anyurl',
             'access_token': 'a4a506440102b8d06a0f63fdd1eadd5f',
             'secret': '66eb2d56a4e930b0e12193b954d6b2e4',
             'warehouse_id': self.warehouse.id}
        )
        self.expected_token = "6b7280eb-e7d4-4b94-a829-7b3853a20126"
        self.expected_user = "1"
        self.expected_account = 1
        self.json_data = {
            'token': {
                'status_code': 200,
                'json': {
                    'token': self.expected_token,
                    'user_id': self.expected_user,
                    'account_id': self.expected_account}},
            'token_fail': {
                'status_code': 400,
                'json': {
                    "error": {
                        "code": 403,
                        "message": "Forbidden"}}},
            'marketplace': {
                'status_code': 200,
                'json': {
                    'admarkt': {
                        'country': 'NLD',
                        'description': 'Admarkt is a Dutch marketplace which'
                                       ' lets you generate qualified traffic'
                                       ' to your online shop.',
                        'homepage': 'http://www.marktplaatszakelijk.nl/'
                                    'admarkt/',
                        'logo': 'cdn/partners//_.jpeg',
                        'name': 'Admarkt',
                        'orders': {'actions': {},
                                   'carriers': {},
                                   'status': {}}},
                    'amazon_fr': {
                        'country': 'FRA',
                        'description': 'Coming soon : description',
                        'homepage': 'http://www.amazon.com/',
                        'logo': 'http://psp-img.gamergen.com/'
                                'amazon-fr-logo_027200C800342974.jpg',
                        'name': 'Amazon FR',
                        'orders': {
                            'actions': {
                                'accept': {
                                    'args': [],
                                    'optional_args': [],
                                    'status': ['new']},
                                'cancel': {
                                    'args': ['cancel_reason'],
                                    'optional_args': [],
                                    'status': ['new',
                                               'waiting_shipment',
                                               'shipped']},
                                'partially_cancel': {
                                    'args': ['line', 'cancel_reason'],
                                    'optional_args': [],
                                    'status': ['new',
                                               'waiting_shipment']},
                                'partially_refund': {
                                    'args': ['line', 'refund_reason'],
                                    'optional_args': [],
                                    'status': ['shipped']},
                                'ship': {
                                    'args': [],
                                    'optional_args': ['line',
                                                      'shipping_date',
                                                      'carrier',
                                                      'tracking_number',
                                                      'shipping_method'],
                                    'status': ['waiting_shipment']}},
                            'carriers': {},
                            'status': {
                                'canceled': ['Canceled'],
                                'new': ['PendingAvailability', 'Pending'],
                                'shipped': ['Shipped', 'InvoiceUnconfirmed'],
                                'waiting_shipment': ['Unshipped',
                                                     'PartiallyShipped',
                                                     'Unfulfillable']}}}}}}
