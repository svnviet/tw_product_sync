from odoo import models, api

var = {'08-Pure': ['White'],
	   '10-Ivory': ['White'],
	   '09-Whisper': ['Brown', 'Yellow'],
	   '12-Sand': ['Brown', 'Yellow'],
	   '24-Garnet': ['Red'],
	   '31-Bronze': ['Brown'],
	   '32-Sponge': ['Yellow'],
	   '30-Emerald': ['Green'],
	   '02-Ash': ['Gray'],
	   '01-Nigth': ['Black'],
	   '03-Feather': ['white'],
	   '06-Linen': ['Brown'],
	   '07-Ivory': ['white', 'Orange'],
	   'Natural': ['White'],
	   'Duckegg/Aqua': ['Blue'],
	   'Red': ['Red'],
	   '13-Stucco': ['Brown'],
	   '33-Linen': ['Brown'],
	   'Purple': ['Purple'],
	   'Orange/Terra': ['Orange'],
	   'Brown': ['Brown'],
	   'White/Ecru': ['white'],
	   '01-Almond': ['Brown', 'White'],
	   '01-Fresco': ['Brown', 'Yellow', 'Red'],
	   '03-Raffia': ['Brown'],
	   '04-Wool': ['brown'],
	   '04-Feather': ['white', 'Gray'],
	   '05-Pearl': ['Yellow', 'White', 'Brown'],
	   '06-Pure': ['Brown'],
	   '08-Snow': ['Gray', 'Black'],
	   '08-Silver': ['Gray'],
	   '10-Gargoyle': ['Gray'],
	   '1-Flint': ['Gray'],
	   '12-Pinecone': ['Black', 'Green'],
	   '14-Fungi': ['White', 'Red'],
	   '15-Cloud': ['Gray', 'Blue'],
	   '26-Marine': ['Blue'],
	   '25-Emerald': ['Blue'],
	   'Blue': ['Blue'],
	   '35-Ice': ['White', 'Blue'],
	   '55-Nigth': ['Blue'],
	   'Grey': ['Gray'],
	   'Gold/Yellow': ['Yellow', 'Orange'],
	   '38-Sesame': ['Brown'],
	   'Indigo': ['Blue'],
	   'Pink': ['Pink'],
	   'Black': ['Black'],
	   'Green': ['Green'],
	   '21-Ink': ['Blue', 'Gray'],
	   '20-Pebble': ['Gray', 'Brown'],
	   '03-Sand': ['Brown', 'Yellow'],
	   '25-Cintronelle': ['Yellow', 'Orange'],
	   '02-Plaza': ['Brown'],
	   '35-Lilac': ['Purple'],
	   '05-Elephant': ['Gray', 'Brown'],
	   '07-Celadon': ['Green', 'Blue'],
	   '07-Mouse': ['Gray', 'Brown'],
	   '05-Hydro': ['Gray', 'Blue'],
	   '09-Desert': ['Brown', 'Gray'],
	   '09-Pearl': ['White', 'Gray'],
	   '09-Swan': ['White'],
	   '14-Caviar': ['Black'],
	   '15-Cement': ['Gray'],
	   'Verde': ['Green'],
	   '14-Zinc': ['Gray'],
	   '02-Petrol': ['Black', 'Blue', ''],
	   '22-Aluminium': ['Gray'],
	   '18-River': ['White', 'Blue'],
	   '01-Dune': ['Brown'],
	   'Beige': ['White', 'Yellow'],
	   '22-Marine': ['Blue'],
	   '03-Sesame': ['Yellow', 'White'],
	   '08-Hazel': ['Brown'],
	   'Gris': ['Gray'],
	   'Azulverde': ['Green', 'Blue'],
	   'Amarillo': ['Yellow', 'Orange'],
	   'Rojo': ['Red'],
	   'Blanco': ['White'],
	   'Grispardo': ['Gray'],
	   '03-Silver': ['Gray'],
	   '03-Mirage': ['Gray'],
	   '03-Ice': ['White', 'Yellow'],
	   '04-Moonlight': ['Black'],
	   '01-Sterling': ['Brown', 'Red'],
	   '4-Raffia': ['Brown'],
	   '01-Metallic': ['Gray'],
	   '05-Cloud': ['White', 'Blue'],
	   '36-Cream': ['White', 'Orange'],
	   '02-Zinc': ['Gray'],
	   '11-Aluminium': ['Gray'],
	   '21-Sesame': ['White', 'Yellow'],
	   '20-Frost': ['White', 'Blue'],
	   '07-Marshmallow': ['White'],
	   '01-Snow': ['White'],
	   '04-Calico': ['White', 'yellow'],
	   '01-Ivory': ['White', 'Yellow'],
	   '34-Natural': ['White'],
	   '36-Flint': ['White'],
	   '01-Ice': ['White'],
	   '01-Silver': ['Gray'],
	   '04-Pure': ['White', 'blue'],
	   '04-Sesame': ['White', 'Brown'],
	   '04-Marzipan': ['White', 'Yellow'],
	   '05-Ivory': ['Yellow', 'Orange'],
	   '12-Steel': ['Gray'],
	   '09-Flax': ['Brown', 'Yellow'],
	   '12-Misty-Gray': ['Blue'],
	   '12-Alabaster': ['White', 'orange', 'yellow'],
	   '13-Griffin': ['Gray', 'Brown'],
	   '13-Pearl': ['White', 'Brown'],
	   '14-Wool': ['Blue', 'Black'],
	   '18-Fog': ['Brown', 'Gray']}

class ProductAttribute(models.Model):
	_inherit = 'product.attribute'


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	def update_family_color(self):
		""" Update family color following var list mapping color """
		product_attribute_value = self.env['product.attribute.value']
		product_color = self.attribute_line_desc_ids.search(['attribute_id.name', '=', 'Color'])
		product_attribute_color = self.env['product.attribute'].search(['name', '=', 'Family Color'])
		product_family_color = self.attribute_line_desc_ids.search(['attribute_id.name', '=', 'Family Color'])
		product_family_color_value_ids = []
		if not product_color:
			return False
		if not product_family_color:
			self.write({
				'attribute_line_desc_ids': (4, product_attribute_color.id)
			})

		color_name_list = [val.name.replace(' ', '') for val in product_color.value_ids]
		for color in color_name_list:
			if color not in var:
				continue
			family_color_list = var[color]
			for family_color in family_color_list:
				attribute_value_id = product_attribute_value.search(['name', '=', family_color])
				if not attribute_value_id:
					attribute_value_id = product_attribute_value.create({
						'name': color
					})
				product_family_color_value_ids.append(attribute_value_id)
		if not product_family_color_value_ids:
			return False

		product_family_color.value_ids = (6, 0, [pc.id for pc in product_family_color_value_ids])